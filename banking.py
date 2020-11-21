import sys
from random import randint
import sqlite3


conn = sqlite3.connect('card.s3db')
cur = conn.cursor()
cur.execute('CREATE TABLE IF NOT EXISTS card (id INTEGER PRIMARY KEY, number TEXT, pin TEXT, balance INTEGER DEFAULT 0);')

user_login_state = False
log_into_account_input_cardnum = ''
log_into_account_input_pin = ''


def menu():
    if not user_login_state:
        print("""
1. Create an account
2. Log into account
0. Exit
        """)
    else:
        print("""
1. Balance
2. Add income
3. Do transfer
4. Close account
5. Log out
0. Exit
        """)


def luhn_algorithm(fifteen_digit_num):
    strinum = fifteen_digit_num
    reversed_string = strinum[len(strinum)::-1]
    reversed_string_to_int = [int(i) for i in reversed_string]
    double_odd = [i * 2 for i in reversed_string_to_int[0::2]]
    deduct_nine_from_big_double_odd = [i - 9 if i > 9 else i for i in double_odd]
    even = [i for i in reversed_string_to_int[1::2]]
    merger_odd_even = deduct_nine_from_big_double_odd + even
    if (((sum(merger_odd_even) % 10) - 10) * -1) == 10:
        return "0"
    else:
        cs = ((sum(merger_odd_even) % 10) - 10) * -1
        return str(cs)


def create_an_account():
    bin_num = '400000'
    account_identifier = ''.join(map(str, [randint(0, 9) for _i in range(9)]))
    checksum = luhn_algorithm(bin_num + account_identifier)
    account_number = bin_num + account_identifier + checksum
    pin = ''.join(map(str, [randint(0, 9) for _i in range(4)]))
    params = (account_number, pin)
    cur.execute("INSERT INTO card (number, pin) VALUES (?, ?)", params)
    conn.commit()
    print("\nYour card has been created")
    print(account_number)
    print("Your card PIN:")
    print(pin)


def log_into_account():
    global log_into_account_input_cardnum
    global log_into_account_input_pin
    n = 0
    p = 0
    print('\nEnter your card number:')
    log_into_account_input_cardnum = input()
    print('Enter your PIN:')
    log_into_account_input_pin = input()
    params = (log_into_account_input_cardnum, log_into_account_input_pin)
    cur.execute("SELECT number, pin FROM card WHERE number = ? AND pin = ?", params)
    row = cur.fetchall()
    for i in row:
        n = i[0]
        p = i[1]
    if n and p:
        print('\nYou have successfully logged in!')
        global user_login_state
        user_login_state = True
        while True:
            menu()
            logged_user_input = input()
            if logged_user_input == '1':
                check_balance = "SELECT balance FROM card WHERE number = ? AND pin = ?"
                cur.execute(check_balance, params)
                result = cur.fetchall()
                for i in result:
                    print(i[0])
            elif logged_user_input == '2':
                print('Enter income:')
                entered_income = int(input())
                check_balance = "SELECT balance FROM card WHERE number = ? AND pin = ?"
                cur.execute(check_balance, (log_into_account_input_cardnum, log_into_account_input_pin))
                old_balance = cur.fetchone()
                new_balance = old_balance[0] + entered_income
                update_balance = "UPDATE card SET balance = ? WHERE number = ? AND pin = ?"
                cur.execute(update_balance, (new_balance, log_into_account_input_cardnum, log_into_account_input_pin))
                conn.commit()
                print('Income was added!')
            elif logged_user_input == '3':
                print('Transfer')
                print('Enter card number:')
                reciever_cardnumber = input()
                reciever_cardnumber_tochars = [char for char in reciever_cardnumber]
                reciever_cardnumber_last_char = reciever_cardnumber_tochars[15]
                reciever_cardnumber_fifteen_dig_tmp = reciever_cardnumber_tochars[0:15]
                reciever_cardnumber_fifteen_dig = ''
                reciever_cardnumber_fifteen_dig.join(reciever_cardnumber_fifteen_dig_tmp)
                tmp = cur.execute("SELECT id FROM card WHERE number = ?", (reciever_cardnumber,))
                data = tmp.fetchone()
                if reciever_cardnumber == log_into_account_input_cardnum:
                    print("You can't transfer money to the same account!")
                    pass
                elif luhn_algorithm(reciever_cardnumber_fifteen_dig.join(reciever_cardnumber_fifteen_dig_tmp)) != reciever_cardnumber_last_char:
                    print("Probably you made a mistake in the card number. Please try again!")
                    pass
                elif data is None:
                    print("Such a card does not exist.")
                    # cur.close()
                    pass
                else:
                    print("Enter how much money you want to transfer:")
                    amount_to_transfer = int(input())
                    get_balance = "SELECT balance FROM card WHERE number = ? AND pin = ?"
                    balance = cur.execute(get_balance, (log_into_account_input_cardnum, log_into_account_input_pin))
                    my_account_balance = balance.fetchone()
                    if my_account_balance[0] < amount_to_transfer:
                        print('Not enough money!')
                    else:
                        check_reciever_balance = "SELECT balance FROM card WHERE number = ?"
                        old_reciever_balance = cur.execute(check_reciever_balance, (reciever_cardnumber,)).fetchone()
                        my_subtructed_balance = my_account_balance[0] - amount_to_transfer
                        augmented_reciever_balance = old_reciever_balance[0] + amount_to_transfer
                        update_reciever_balance = "UPDATE card SET balance = ? WHERE number = ?"
                        cur.execute(update_reciever_balance, (augmented_reciever_balance, reciever_cardnumber))
                        conn.commit()
                        update_my_balance = "UPDATE card SET balance = ? WHERE number = ? AND pin = ?"
                        cur.execute(update_my_balance, (my_subtructed_balance, log_into_account_input_cardnum, log_into_account_input_pin))
                        conn.commit()
                        print('Success!')
            elif logged_user_input == '4':
                account_to_close = "DELETE FROM card WHERE number = ? AND pin = ?"
                cur.execute(account_to_close, (log_into_account_input_cardnum, log_into_account_input_pin))
                conn.commit()
                print('The account has been closed!')
                user_login_state = False
                break
            elif logged_user_input == '5':
                user_login_state = False
                print('\nYou have successfully logged out!')
                # conn.close()
                break
            elif logged_user_input == '0':
                user_login_state = False
                print('\nBye!')
                # conn.close()
                sys.exit()
    else:
        print('Wrong card number or PIN!')


while True:
    menu()
    user_input = int(input())
    if user_input == 1:
        create_an_account()
    elif user_input == 2:
        log_into_account()
    elif user_input == 0:
        print('\nBye!')
        # conn.close()
        break
