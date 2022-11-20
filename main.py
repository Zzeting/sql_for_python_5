import psycopg2

# conn = psycopg2.connect(database='postgres', user='postgres', password='1234567890', host='localhost', port='5434')
with psycopg2.connect(database='postgres', user='postgres', password='1234567890', host='localhost', port='5434') as conn:
    with conn.cursor() as cur:
        def create_DB(cursor):

            cursor.execute("""
                drop schema if exists "clients" cascade;
                
                create schema "clients";
                
                set search_path to clients;
                """)

            cursor.execute("""
               create table clients(
                    id serial primary key,
                    first_name varchar(50) not null,
                    last_name varchar(50) not null,
                    email varchar(100) not null unique,
                    phone text[]
                );
                """)

        def insert_new_clients(cursor, first_name, last_name, email, phone=[]):
            cursor.execute("""
                insert into clients (first_name, last_name, email, phone)
                values (%s, %s, %s, %s)""", (first_name, last_name, email, phone))

        def add_phone_clients(cursor, id, phone):
            cursor.execute("""
                select phone
                from clients
                where id = %s
            """, (id,))
            phones = cursor.fetchone()[0]
            if phone not in phones:
                cursor.execute("""
                update clients
                set phone = array_append(phone, %s)
                where id = %s
                """, (phone, id))
            else:
                print('Вы уже добавили этот номер')

        def change_info_clients(cursor, id, first_name=None, last_name=None, email=None, phone=None):
            if first_name is not None:
                cursor.execute("""
                    update clients
                    set first_name = %s
                    where id = %s
                    """, (first_name, id))
            if last_name is not None:
                cursor.execute("""
                    update clients
                    set last_name = %s
                    where id = %s
                    """, (last_name, id))
            if email is not None:
                cursor.execute("""
                    update clients
                    set email = %s
                    where id = %s
                    """, (email, id))
            if phone is not None:
                cursor.execute("""
                    select phone
                    from clients
                    where id = %s
                """, (id,))
                phones = cursor.fetchone()[0]
                if len(phones) > 0:
                    print('Номера клиента: ')
                    for ph in phones:
                        print(ph)
                    change_phone = input("Введите номер, который хотите заменить... ")
                    try:
                        phones.remove(change_phone)
                        phones.append(phone)
                        cursor.execute("""
                                       update clients
                                       set phone = %s
                                       where id = %s
                                       """, (phones, id))
                    except ValueError:
                        print('Данного номера в списке нет')
                else:
                    cursor.execute("""
                        update clients
                        set phone = %s
                        where id = %s
                        """, ([phone], id))

        def drop_phone_clients(cursor, id, phone):
            cursor.execute("""
                            select phone
                            from clients
                            where id = %s
                        """, (id,))
            phones = cursor.fetchone()[0]
            if phone in phones:
                phones.remove(phone)
                cursor.execute("""
                            update clients
                            set phone = %s
                            where id = %s
                            """, (phones, id))
            else:
                print('Данного номера в списке нет')

        def delete_clients(cursor, id):
            cursor.execute("""
                delete from clients
                where id = %s
            """, (id,))

        def select_clients(cursor, first_name=None, last_name=None, email=None, phone=None):
            search_atrr = {}
            values = []
            s = 'select * from clients where'
            if first_name is not None:
                search_atrr['first_name'] = first_name
            if last_name is not None:
                search_atrr['last_name'] = last_name
            if email is not None:
                search_atrr['email'] = email
            if phone is not None:
                s += ' %s <@ (phone) and'
                values.append(phone)
            for atrb, val in search_atrr.items():
                s += f" {atrb} = %s and"
                values.append(val)
            s = s[:-4]
            cursor.execute(s, values)
            return cursor.fetchall()

        # Функция, создающая структуру БД (таблицы)
        # создается одна таблица, так как номера телефонов можно хранить в одном массиве данных одного клиента
        create_DB(cur)

        # Функция, позволяющая добавить нового клиента
        insert_new_clients(cur, first_name='Aleks', last_name='Mamontov', email='mamontov@mail.ru',
                           phone=['89621021102', '89652365454'])
        insert_new_clients(cur, first_name='Aleks', last_name='Giglin', email='gilin@mail.ru',
                           phone=['86554658322'])

        # Функция, позволяющая добавить телефон для существующего клиента
        add_phone_clients(cur, 1, '89625656366')

        # Функция, позволяющая изменить данные о клиенте
        change_info_clients(cur, 1, first_name='Алексей', email='ale@mail.ru', phone='89144195726')

        # Функция, позволяющая удалить телефон для существующего клиента
        drop_phone_clients(cur, 1, '89652365454')

        # Функция, позволяющая удалить существующего клиента
        delete_clients(cur, 2)

        # Функция, позволяющая найти клиента по его данным (имени, фамилии, email-у или телефону)
        search = select_clients(cur, first_name='Алексей', last_name='Mamontov', phone=['89144195726'])
        print(search)
