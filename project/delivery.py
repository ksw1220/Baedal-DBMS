import time
import argparse
import datetime
from helpers.connection import conn

def main(args):
    if args.function == "status":
        try:
            cur = conn.cursor()
            if args.e:
                now_time = datetime.datetime.now()
                sql = "UPDATE orders SET status = 2, delivered_time = %(d_time)s WHERE did = %(id)s AND id = %(order_id)s;"
                cur.execute(sql, {
                    "id": args.id,
                    "d_time": now_time,
                    "order_id": args.e
                })
                conn.commit()
                
                sql = "UPDATE delivery SET stock = stock - 1 WHERE id = %(id)s;"
                cur.execute(sql,{"id":args.id})
                conn.commit()
            elif args.a:
                sql = "SELECT * FROM orders WHERE did = %(id)s"
                cur.execute(sql,{"id":args.id})
                rows = cur.fetchall()

                print("Delivery status | Order id")
                print("--------------------------")
                for row in rows:
                    if row[9]==0:
                        status = "pending"
                    elif row[9]==1:
                        status = "delivering"
                    elif row[9]==2:
                        status = "delivered"
                    
                    print("%-16s     %d"%(status,row[0]))
            else:
                sql = "SELECT * FROM orders WHERE did = %(id)s AND status = 1"
                cur.execute(sql,{"id":args.id})
                rows = cur.fetchall()

                print("Delivery status | Order id")
                print("--------------------------")
                status = "delivering"
                for row in rows:
                    print("%-16s     %d"%(status,row[0]))
        except Exception as err:
            print(err)
        pass

if __name__ == "__main__":
    start = time.time()
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(help='Command of Function')

    parser_status = subparsers.add_parser('status', help='Info of Delivery')
    parser_status.add_argument('function', action='store_const', const='status', help='Funtion of Command')
    parser_status.add_argument('id', type=int, help='ID of Delivery')
    parser_status.add_argument('-e', type=int, help='Complete Delivery')
    parser_status.add_argument('-a', action="store_true", help='List of All Delivery')
    
    args = parser.parse_args()
    # print(args)
    print("")
    main(args)
    print("")
    print("Running Time: ", end="")
    print(time.time() - start)
