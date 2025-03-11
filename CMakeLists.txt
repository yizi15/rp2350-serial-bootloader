# Derived from the Pico SDK, which carries the following
# LICENSE.txt:
# Copyright 2020 (c) 2020 Raspberry Pi (Trading) Ltd.
#
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the
# following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following
#    disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following
#    disclaimer in the documentation and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products
#    derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF
# THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

cmake_minimum_required(VERSION 3.13)

set(PICO_PLATFORM "rp2350")

set(PICO_BOARD "none")
set(PICO_CMSIS_DEVICE RP2350)

include(pico_sdk_import.cmake)

project(test_project C CXX ASM)

set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 17)

pico_sdk_init()

# Build the bootloader as a standalone thing

add_executable(bootloader main.c)

# add_definitions(-DDEBUG)
# add_definitions(-DPICO_DEFAULT_UART_TX_PIN=44 -DPICO_DEFAULT_UART_RX_PIN=45)
# add_definitions(-DPICO_DEFAULT_UART=0)
# add_definitions(-DPICO_DEFAULT_UART_BAUD_RATE=921600)

function(target_cl_options option)
    target_compile_options(bootloader PRIVATE ${option})
    target_link_options(bootloader PRIVATE ${option})
endfunction()

target_cl_options("-Os")
target_cl_options("-ffunction-sections")
target_cl_options("-fdata-sections")
target_link_options(bootloader PRIVATE "LINKER:--gc-sections")

pico_add_bin_output(bootloader)
#pico_set_binary_type(bootloader copy_to_ram)

set_target_properties(bootloader PROPERTIES COMPILE_FLAGS "-Wall")

#pico_set_linker_script(bootloader ${CMAKE_CURRENT_SOURCE_DIR}/bootloader.ld)

target_link_libraries(bootloader
                      pico_stdlib
                      hardware_dma
                      hardware_flash
                      hardware_structs
                      hardware_resets
                      cmsis_core)

set(BOOTLOADER_DIR "${CMAKE_CURRENT_LIST_DIR}" CACHE INTERNAL "")

# Build a library to embed into applications

function(bootloader_define_library)
	set(NAME bootloader)
	set(ORIGINAL_BIN ${CMAKE_CURRENT_BINARY_DIR}/${NAME}.bin)
	set(BIN_ASM ${CMAKE_CURRENT_BINARY_DIR}/${NAME}_bin.S)

	add_custom_target(${NAME}_bin DEPENDS ${ORIGINAL_BIN})
	add_custom_command(OUTPUT ${ORIGINAL_BIN} DEPENDS ${NAME} COMMAND ${CMAKE_OBJCOPY} -Obinary $<TARGET_FILE:${NAME}> ${ORIGINAL_BIN})

	find_package (Python3 REQUIRED COMPONENTS Interpreter)
	add_custom_target(${NAME}_bin_asm DEPENDS ${BIN_ASM})
	add_custom_command(OUTPUT ${BIN_ASM} DEPENDS ${ORIGINAL_BIN}
		COMMAND ${Python3_EXECUTABLE} ${BOOTLOADER_DIR}/mkasm.py ${ORIGINAL_BIN} ${BIN_ASM}
	)

	add_library(${NAME}_library INTERFACE)
	add_dependencies(${NAME}_library ${NAME}_bin_asm)
	# not strictly (or indeed actually) a link library, but this avoids dependency cycle
	target_link_libraries(${NAME}_library INTERFACE ${BIN_ASM})
endfunction()

bootloader_define_library()

# Provide a helper to build a combined target
function(bootloader_build_combined NAME)
	set(APP_BIN ${CMAKE_CURRENT_BINARY_DIR}/${NAME}.bin)

	set(COMBINED ${NAME}_combined)

	target_link_libraries(${NAME} PRIVATE bootloader_library)

	pico_set_linker_script(${NAME} ${BOOTLOADER_DIR}/combined.ld)

	pico_add_bin_output(${NAME})
	message(${APP_BIN})

	add_custom_target(${COMBINED} DEPENDS ${CMAKE_CURRENT_BINARY_DIR}/${COMBINED}.elf)
	add_custom_command(OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/${COMBINED}.elf DEPENDS ${APP_BIN}
	COMMAND ${Python3_EXECUTABLE} ${BOOTLOADER_DIR}/combined.py ${NAME} ${CMAKE_CURRENT_BINARY_DIR} ${CMAKE_OBJCOPY})

endfunction()

# Provide a helper to build a standalone target

function(bootloader_build_standalone NAME)
	pico_set_linker_script(${NAME} ${BOOTLOADER_DIR}/standalone.ld)
	pico_add_bin_output(${NAME})
endfunction()
