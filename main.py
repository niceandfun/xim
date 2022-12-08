from ticket_utils.ticket_parser import Ticket

if __name__ == '__main__':
    etalon_file = 'source/etalon.pdf'
    ticket_file = 'source/test_task.pdf'

    etalon = Ticket(etalon_file, etalon=True)

    print(etalon)  # вывод информации о билете в виде словаря
    print(etalon.ticket_info)  # вывод информации о билете в виде словаря

    ticket = Ticket(ticket_file)

    print(ticket)  # вывод информации о билете в виде словаря
    print(ticket.ticket_info)  # вывод информации о билете в виде словаря

    print(etalon == ticket)  # сравнение билетов
    print(ticket == etalon)  # сравнение билетов
