import paramiko
from datetime import datetime


def connection(host: str, port: int, login: str, password: str):
    """Подключается по SSH с помощью логина и пароля"""

    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, port, login, password)


def lsblk():
    """Показывает есть ли флешка в ПЛК"""

    stdin, stdout, stderr = ssh.exec_command('lsblk')
    lines = stdout.readlines()
    find_sd_card = list()
    for i in range(len(lines)):
        find_sd_card.append(lines[i].find('mmcblk0p1'))
    find_sd_card.sort(reverse=True)
    if find_sd_card[0] != -1:  # Если флешка есть, то начинаем проверку на наличие скриптов
        print('SD CARD IN PLC')
        crontab()
    else:
        return print('NO SD CARD IN PLC')


def crontab():
    """Проверяет есть ли скрипты arch_logs и arch_data"""

    stdin, stdout, stderr = ssh.exec_command('crontab -l')
    lines_out = stdout.readlines()
    flag_data_presence = False
    flag_logs_presence = False
    logs = list()
    data = list()
    for i in range(len(lines_out)):
        logs.append(lines_out[i].find('arch_logs.sh'))
        data.append(lines_out[i].find('arch_data.sh'))
    logs.sort(reverse=True)
    data.sort(reverse=True)
    if logs[0] != -1:
        flag_logs_presence = True
    if data[0] != -1:
        flag_data_presence = True
    if flag_logs_presence and flag_data_presence:  # Если скрипты есть, начинаем проверку на наличие переменной флешки
        print('data.sh and logs.sh is created')
        search_sd_card()
    elif not flag_data_presence and flag_logs_presence:
        print('data.sh not created')
        search_sd_card()  # Если одо из скриптов нет, то начинаем проверку на переменную sd_card
    else:
        return print('not created arch')


def search_sd_card():
    """Проверяет есть ли переменная sd_card в скриптах"""

    stdin, stdout, stderr = ssh.exec_command('cat /work/gsrv/sys_scripts/arch_data.sh | grep sd_card')
    stdin1, stdout1, stderr1 = ssh.exec_command('cat /work/gsrv/sys_scripts/arch_logs.sh | grep sd_card')
    lines = stdout.readlines()
    lines1 = stdout1.readlines()
    print(lines, lines1)
    if lines and lines1:
        stdin, stdout, stderr = ssh.exec_command('ls /work/')
        lines = stdout.readlines()
        search_dir_sd_card(lines=lines)  # Если скрипты есть, начинаем проверку на папку sd_card
    else:
        return 0


def search_dir_sd_card(lines):
    """Проверяет наличие папки sd_card в /work/"""

    flag_sd_card_search = False
    for i in range(len(lines)):
        if lines[i].find('sd_card') != -1:
            flag_sd_card_search = True
    if not flag_sd_card_search:
        print('Нет папки sd_card')  # Если нет такой папки, то создаем
        ssh.exec_command('mount / -o remount,rw')
        ssh.exec_command('mkdir /work/sd_card')
        ssh.exec_command('mount / -o remount,ro')
        mount_mnt()
        ssh.exec_command('/work/gsrv/sys_scripts/arch_logs.sh > /dev/null 2>&1')
        ls()
    else:
        mount_mnt()
        ssh.exec_command('/work/gsrv/sys_scripts/arch_logs.sh > /dev/null 2>&1')
        ls()


def mount_mnt():
    """Монтирует /mnt"""

    ssh.exec_command('mount /dev/mmcblk0p1 /mnt')


def umount():
    """Демонтирует /mnt"""

    ssh.exec_command('umount /dev/mmcblk0p1')


def ls():
    """Показывает содержимое папки со временем изменения"""

    mount_mnt()
    stdin, stdout, stderr = ssh.exec_command('ls /mnt/arch/logs -l')
    global lines
    lines = stdout.readlines()
    print(stdout.readlines())
    return lines


def date_in_line(lines_ls: list):
    counter = 0
    date_line = ''
    for i in lines_ls[1]:
        if i == ' ':
            counter += 1
        if counter == 5 or counter == 6 or counter == 7:
            date_line += i
    return print(date_line.replace(' ', '', 1))


def compare_date():
    date_line = str(datetime.utcnow())[8] + str(datetime.utcnow())[9]
    print(date_line, datetime.utcnow())


lines = list()
ssh = paramiko.SSHClient()

host = "178.176.43.109"
port = 20022
username = "root"
password = "soyuz2000root12345"

connection(host=host, port=port, login=username, password=password)
lsblk()
#print(len(lines))
#date_in_line(lines_ls=lines)
umount()
#compare_date()
