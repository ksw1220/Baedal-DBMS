import time
import argparse
from helpers.connection import conn

def main(args):
    try:
        cur = conn.cursor()
        if args.function == "info":
            sql = "SELECT NAME, PHONE, LOCAL, DOMAIN FROM seller WHERE id=%(id)s;"
            cur.execute(sql, {"id": args.id})
            rows = cur.fetchall()
            for row in rows:
                print("Name: ", row[0])
                print("Phone Number: ", row[1])
                print("email: ", row[2], "@", row[3])
        elif args.function == "update":
            sql = "UPDATE seller SET " + args.property +"=%(value)s WHERE id=%(id)s;"
            cur.execute(sql, {
                "value": args.value,
                "id": args.id
            })
            conn.commit()
    except Exception as err:
        err="Invalid Input"
        print(err)
    pass

if __name__ == "__main__":
    start = time.time()
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(help='Command of Function')

    # info
    parser_info = subparsers.add_parser('info', help='Info of seller')
    parser_info.add_argument('function', action='store_const', const='info',help='Funtion of Command')
    parser_info.add_argument('id', type=int, help='ID of Seller')

    # update
    parser_update = subparsers.add_parser('update',help='Update seller')
    parser_update.add_argument('function', action='store_const', const='update',help='Funtion of Command')
    parser_update.add_argument('id', type=int, help='ID of Seller')
    parser_update.add_argument("property", nargs="?",type = str, help="Property to Change")
    parser_update.add_argument("value", nargs="?", help="Value to Change")

    args = parser.parse_args()
    print("")
    main(args)
    print("")
    print("Running Time: ", end="")
    print(time.time() - start)
