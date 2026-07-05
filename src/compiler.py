import sys
import os

OP_HALT   = 0
OP_PUSH   = 1
OP_ADD    = 2
OP_OUT    = 3
OP_STORE  = 4
OP_LOAD   = 5
OP_SYSTEM = 6
OP_JIF    = 7
OP_EQ     = 8

def compile_fax(source_code):
    bytecode = []
    variables = {}
    next_var_idx = 0

    lines = source_code.split('\n')
    
    for line_num, line in enumerate(lines, 1):
        line = line.strip().lstrip('\xef\xbb\xbf')
        if not line or line.startswith('//'):
            continue
            
        # 1. Обработка команды SYSTEM
        if line.startswith('system '):
            # Извлекаем то, что находится внутри кавычек ""
            try:
                cmd_text = line.split('"')[1]
            except IndexError:
                print(f"Ошибка (строка {line_num}): пропущены кавычки в команде system")
                return None
                
            # Переводим всю строку в байты кодировки cp866 (поддерживает русский язык в консоли Windows)
            cmd_bytes = cmd_text.encode('cp866') 
            
            bytecode.append(OP_SYSTEM)
            bytecode.append(len(cmd_bytes)) # Пишем длину именно в байтах
            for b in cmd_bytes:
                bytecode.append(b)          # Записываем готовые байты (они точно от 0 до 255!)
            continue

        parts = line.split()
        command = parts[0].strip().lower()

        if command == 'write':
            var_name = parts[1]
            value = parts[2]
            if var_name not in variables:
                variables[var_name] = next_var_idx
                next_var_idx += 1
            bytecode.append(OP_PUSH)
            bytecode.append(int(value))
            bytecode.append(OP_STORE)
            bytecode.append(variables[var_name])

        # Не забудь в начале компилятора объявить OP_JIF = 7, если еще не сделал!

        if command == 'push':
            arg = int(parts[1])
            bytecode.append(OP_PUSH)  # Никаких запятых после скобки!
            bytecode.append(arg)
            continue

        elif command == 'add':
            bytecode.append(OP_ADD)   # Чётко, без запятой!
            continue

        elif command == 'eq':
            bytecode.append(OP_EQ)
            continue

        elif command == 'jif':
            arg = int(parts[1])
            bytecode.append(OP_JIF)
            bytecode.append(arg)
            continue

        elif command == 'halt':       # Или как у тебя называется конец программы
            bytecode.append(OP_HALT)
            continue
            
        elif command == 'out':
            if '+' in parts:
                plus_idx = parts.index('+')
                left_operand = parts[plus_idx - 1]
                right_operand = parts[plus_idx + 1]
                
                if left_operand.isdigit():
                    bytecode.append(OP_PUSH)
                    bytecode.append(int(left_operand))
                else:
                    bytecode.append(OP_LOAD)
                    bytecode.append(variables[left_operand])
                
                if right_operand.isdigit():
                    bytecode.append(OP_PUSH)
                    bytecode.append(int(right_operand))
                else:
                    bytecode.append(OP_LOAD)
                    bytecode.append(variables[right_operand])
                
                bytecode.append(OP_ADD)
                bytecode.append(OP_OUT)
            else:
                arg = parts[1]
                if arg.isdigit():
                    bytecode.append(OP_PUSH)
                    bytecode.append(int(arg))
                else:
                    bytecode.append(OP_LOAD)
                    bytecode.append(variables[arg])
                bytecode.append(OP_OUT)
        else:
            print(f"Ошибка (строка {line_num}): неизвестная команда '{command}'")
            return None
            
    bytecode.append(OP_HALT)
    print(bytecode)
    return bytes(bytecode)

if __name__ == '__main__':
    # Сразу создадим крутой тестовый скрипт
    #with open("main.fax", "w") as f:
       # f.write("// Проверяем команду system!\n")
       # f.write("system \"echo --- Запускаем системную команду из fax! ---\"\n")
      #  f.write("write x 10\n")
       # f.write("out x + 32\n")
       # f.write("system \"dir program.faxc\"\n") # Выведет инфу о скомпилированном файле через cmd
        
     with open("main.fax", "r", encoding='utf-8-sig') as f:
        fax_code = f.read()
    
     print("--- Компиляция файла main.fax с поддержкой system ---")
     binary_data = compile_fax(fax_code)
    
     if binary_data:
         with open("program.faxc", "wb") as f:
             f.write(binary_data)
         print("Успешно! Байт-код сохранен в 'program.faxc'")
