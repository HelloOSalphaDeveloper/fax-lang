#include <stdio.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

typedef enum {
    OP_HALT   = 0x00,
    OP_PUSH   = 0x01,
    OP_ADD    = 0x02,
    OP_OUT    = 0x03,
    OP_STORE  = 0x04,
    OP_LOAD   = 0x05,
    OP_SYSTEM = 0x06,
    OP_JIF    = 0x07,  // Добавили в Си
    OP_EQ     = 0x08
} OpCode;

int main() {
    system("chcp 65001 > nul");

    FILE *file = fopen("program.faxc", "rb");
    if (file == NULL) {
        printf("Ошибка: Не удалось открыть файл program.faxc!\n");
        return 1;
    }

    unsigned char code[1024];
    int code_size = fread(code, 1, sizeof(code), file);
    fclose(file);

    printf("--- Запуск Виртуальной Машины fax ---\n");

    int stack[256];
    int sp = -1;
    int ip = 0;
    int variables[26] = {0};
    bool running = true;

    while (running && ip < code_size) {
        unsigned char instruction = code[ip];
        ip++;

        switch (instruction) {
            case OP_HALT:
                running = false;
                break;
            case OP_PUSH:
                stack[sp++] = code[ip++];
                break;
            case OP_ADD: {
                int b = stack[sp--];
                int a = stack[sp--];
                stack[++sp] = a + b;
                break;
            }
            case OP_OUT:
                printf("[OUT]: %d\n", stack[sp--]);
                break;
            case OP_STORE:
                variables[code[ip++]] = stack[sp--];
                break;
            case OP_LOAD:
                stack[++sp] = variables[code[ip++]];
                break;
                
            // Вот она, магия! Читаем строку прямо из байт-кода
            case OP_SYSTEM: {
                int length = code[ip++]; // Узнаем длину строки
                char cmd_buffer[256];     // Буфер для текста команды
                
                // Копируем символы из байт-кода в буфер
                for (int i = 0; i < length; i++) {
                    cmd_buffer[i] = code[ip++];
                }
                cmd_buffer[length] = '\0'; // Строка в Си должна заканчиваться нулем!
                
                // Вызываем реальную системную команду
                system(cmd_buffer);
                break;
            }
            case OP_JIF: {
                // 1. Считываем адрес прыжка И ОБЯЗАТЕЛЬНО сдвигаем ip на следующий байт!
                int target_address = code[ip++]; 
    
                // 2. Достаем условие со стека
                int condition = stack[--sp]; 
    
                // 3. Если условие выполнено (не ноль) — прыгаем!
                if (condition != 0) {
                    ip = target_address; 
                }
                // Если условие 0, ip уже указывает на следующую за jif команду, перешагнув девятку!
                break;
            }
            case OP_EQ: {
                int b = stack[--sp];
                int a = stack[--sp];
                stack[sp++] = (a == b) ? 1 : 0;
                break;
            }
            
            default:
                printf("Неизвестная команда: 0x%02X\n", instruction);
                running = false;
                break;
        }
    }

    printf("--- Программа успешно завершена ---\n");
    return 0;
}