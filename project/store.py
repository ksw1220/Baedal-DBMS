import time
import argparse
import geopy
from geopy.distance import geodesic
from helpers.connection import conn


def main(args):
    try:
        cur = conn.cursor()
        if args.function == "info":
            sql = "SELECT * FROM store WHERE id=%(id)s;"
            cur.execute(sql, {"id": args.id})
            rows = cur.fetchall()
            for row in rows:
                print("Store Name: ", row[2])
                print("Address: ", row[1])
                print("Phone number: ", end="")
                for j in row[5]:
                    print(j, end=" ")
                print("\n", end="")

        elif args.function == "menu":
            sql = "SELECT * FROM menu WHERE sid=%(id)s;"
            cur.execute(sql, {"id": args.id})
            rows = cur.fetchall()
            for i in range(len(rows)):
                row = str(i+1)+". Menu ID: " + \
                    str(rows[i][0])+", Name: "+rows[i][1]
                print(row)
        elif args.function == "add_menu":
            sql = "INSERT INTO menu (menu, sid) VALUES(%(name)s,%(id)s);"
            cur.execute(sql, {
                "id": args.id,
                "name": args.name
            })
            conn.commit()
            print("Add menu is complete")
        elif args.function == "order":
            # filter 가 없는 경우 모두
            sql = "SELECT * FROM orders WHERE sid = %(id)s;"
            if args.filter:
                if args.filter == '0' or args.filter == 'pending':
                    sql = "SELECT * FROM orders WHERE sid = %(id)s AND status = 0;"
                elif args.filter == '1' or args.filter == 'deliverying':
                    sql = "SELECT * FROM orders WHERE sid = %(id)s AND status = 1;"
                elif args.filter == '2' or args.filter == 'delivered':
                    sql = "SELECT * FROM orders WHERE sid = %(id)s AND status = 2;"
            cur.execute(sql, {
                "id": args.id,
            })
            rows = cur.fetchall()
            print("Orders")
            print("---------")
            for row in rows:
                print("Order ID: ",row[0])
                print("Store ID: ",row[1])
                print("Customer ID:",row[2])
                print("Menu:",row[4])
                print("Payment: ",end="")
                if(row[10]['type']=='card'):
                    print("cardnum = "+str(row[10]['data']['card_num'])+", type = card")
                elif(row[10]['type']=='account'):
                    print("bid = "+str(row[10]['data']['bid'])+", accountnum ="+str(row[10]['data']['acc_num'])+", type = account")
                print("Otime:", row[7])
                print("Dtime:",row[8])
                print("cphone:",row[11])
                print("status:",end=" ")
                if row[9]==0:
                    print("pending")
                elif row[9]==1:
                    print("delivering")
                elif row[9]==2:
                    print("delivered")
                print("------------")
        elif args.function == "update_order":
            # check it is pending
            sql = "SELECT * FROM orders WHERE id = %(order_id)s;"
            cur.execute(sql,{"order_id":args.order_id})
            order = cur.fetchall()[0]

            if order[9] !=0:
                print("Error: Order %d is not pending"%args.order_id)
                return

            sql = "SELECT lat,lng FROM store WHERE id = %(id)s;"
            cur.execute(sql, {"id": args.id,})
            rows = cur.fetchall()

            store_loc = list(rows[0])

            sql = "select id, lat, lng from delivery where stock<=4"
            cur.execute(sql)
            deliveries = cur.fetchall()
       
            print("Wait a second")
            result = []
            for delivery in deliveries:
                delivery_loc = [delivery[1],delivery[2]]
                distance = geodesic(store_loc,delivery_loc)
                result.append((delivery[0],distance))

            result = sorted(result,key=lambda t: t[1])
            delivery_id = result[0][0]

            print("This order is assigned to %d delivery"%delivery_id)
            sql = "UPDATE orders SET status = 1, did = %(did)s WHERE id = %(order_id)s;"
            cur.execute(sql, {
                "id": args.id,
                "did": delivery_id,
                "order_id": args.order_id
            })
            conn.commit()

            sql = "UPDATE delivery SET stock = stock + 1  WHERE id = %(id)s;"
            cur.execute(sql,{"id" : delivery_id,})
            conn.commit()
        elif args.function == "stat":
            sql = "SELECT DATE(order_time), COUNT(order_time) FROM orders WHERE sid = %(id)s AND order_time >= %(start_date)s GROUP BY DATE(order_time) ORDER BY date LIMIT %(days)s;"
            cur.execute(sql, {
                "id": args.id,
                "start_date": args.start_date,
                "days": args.days
            })
            rows = cur.fetchall()
            print("   Date   | Orders")
            for row in rows:
                print(row[0],"  ",row[1])
        elif args.function == "search":
            # store의 메뉴의 개수를 구한다.
            sql = "SELECT count(*) FROM menu WHERE sid = %(id)s;"
            cur.execute(sql,{"id":args.id})
            count = cur.fetchall()[0][0]

            sql = "SELECT cid FROM (SELECT cid,mid FROM orders WHERE sid = %(id)s GROUP BY cid,mid) AS SUB(cid,mid) GROUP BY cid HAVING COUNT(mid)=%(count)s;"
            cur.execute(sql, {
                "id": args.id,
                "count": count
            })
            rows = cur.fetchall()

            print("Customer ID | Customer name")
            print("---------------------------")
            for row in rows:
                cid = row[0]
                sql = "SELECT name FROM customer WHERE id = %(cid)s;"
                cur.execute(sql,{"cid":cid})
                cname = cur.fetchall()[0][0]
                print("%6d      |%8s"%(cid,cname))
    except Exception as err:
        err = "Invalid Input"
        print(err)
    pass
    


if __name__ == "__main__":
    start = time.time()

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(help='Command of Function')

    parser_info = subparsers.add_parser('info', help='Info of Store')
    parser_info.add_argument('function', action='store_const', const='info',help='Funtion of Command')
    parser_info.add_argument('id', type=int, help='ID of Store')

    parser_menu = subparsers.add_parser('menu', help='Menu of Store')
    parser_menu.add_argument('function', action='store_const', const='menu',help='Funtion of Command')
    parser_menu.add_argument('id', type=int, help='ID of Store')

    parser_add_menu = subparsers.add_parser('add_menu', help='Add Menu')
    parser_add_menu.add_argument('function', action='store_const', const='add_menu',help='Funtion of Command')
    parser_add_menu.add_argument('id', type=int, help='ID of Store')
    parser_add_menu.add_argument("name", nargs="?", help="Name of new menu")

    parser_order = subparsers.add_parser('order', help='Add Menu')
    parser_order.add_argument('function', action='store_const', const='order',help='Funtion of Command')
    parser_order.add_argument('id', type=int, help='ID of Store')
    parser_order.add_argument('filter', nargs="?", help='Filter of Order')

    parser_update_order = subparsers.add_parser('update_order', help='Update Order')
    parser_update_order.add_argument('function', action='store_const', const='update_order',help='Funtion of Command')
    parser_update_order.add_argument('id', type=int, help='ID of Store')
    parser_update_order.add_argument('order_id', type=int, help='ID of Orders')

    parser_stat = subparsers.add_parser('stat', help='Stat of Order')
    parser_stat.add_argument('function', action='store_const', const='stat',help='Funtion of Command')
    parser_stat.add_argument('id', type=int, help='ID of Store')
    parser_stat.add_argument('start_date', help='Date to Start')
    parser_stat.add_argument('days', type = int, help='Date to Start')

    parser_search = subparsers.add_parser('search', help='Search of Order')
    parser_search.add_argument('function', action='store_const', const='search',help='Funtion of Command')
    parser_search.add_argument('id', type=int, help='ID of Store')

    args = parser.parse_args()
    print("")
    main(args)
    print("")
    print("Running Time: ", end="")
    print(time.time() - start)
