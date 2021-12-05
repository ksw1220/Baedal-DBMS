import time
import argparse
import json
import geopy
from geopy.distance import geodesic
import datetime
from helpers.connection import conn


def main(args):
    try:
        cur = conn.cursor()
        if args.function == "info":
            sql = "SELECT * FROM customer WHERE id=%(id)s;"
            cur.execute(sql, {"id": args.id})
            rows = cur.fetchall()
            for row in rows:
                print("Info of Customer", row[0])
                print("name:", row[1])
                print("phone:", row[2])
                print("local:", row[3])
                print("domain:", row[4])
                print("password:", row[5])
                print("payments:", end=" ")
                for payment in row[6]:
                    # print(payment['data'])
                    if 'bid' in payment['data']:
                        print(
                            'accountnum =', payment['data']['acc_num'], "type = account", end=" ")
                    else:
                        print(
                            'cardnum =', payment['data']['card_num'], "type = card", end=" ")
                print('\n', end="")
                print("lat/lng:", row[7], row[8])

        elif args.function == "address":
            sql = "SELECT addresses FROM customer WHERE id = %(id)s;"
            cur.execute(sql, {"id": args.id})
            rows = cur.fetchall()

            if args.create:
                if rows[0][0] == None:
                    sql = "UPDATE customer SET addresses[0] = %(address)s " + "WHERE id = %(id)s;"
                else:
                    length = len(rows[0][0])
                    sql = "UPDATE customer SET addresses[" + str(length) + "] = %(address)s " + "WHERE id = %(id)s;"
                cur.execute(sql, {
                    "id": args.id,
                    "address": args.create[0]
                })
            elif args.edit:
                sql = "UPDATE customer SET addresses[%(aid)s] = %(address)s " + "WHERE id = %(id)s;"
                cur.execute(sql, {
                    "id": args.id,
                    "aid": int(args.edit[0]) - 1,
                    "address": args.edit[1]
                })
            elif args.remove:
                tmp = []
                array = rows[0][0]
                del array[args.remove[0]-1]

                if array:
                    for e in array:
                        tmp.append("'" + e + "'")
                    tmp = ','.join(tmp)
                    sql = "UPDATE customer set addresses = ARRAY[" + tmp + "] WHERE id = %(id)s;"
                else:
                    print('b')
                    sql = "UPDATE customer set addresses = null WHERE id = %(id)s;"
                cur.execute(sql, {"id": args.id})
            else:
                if rows[0][0]:
                    print("Address of Customer", args.id)
                    for i in range(len(rows[0][0])):
                        print(str(i + 1) + ".", rows[0][0][i])
                else:
                    print("Customer", args.id, "doesn't have addresses")
            conn.commit()
        elif args.function == "pay":
            sql = "SELECT payments FROM customer WHERE id=%(id)s;"
            cur.execute(sql, {"id": args.id})
            rows = cur.fetchall()

            payments = rows[0][0]

            if args.add_card:
                new_card = {'data':{'card_num':args.add_card[0]},'type':'card'}
                payments.append(new_card)
            elif args.add_account:
                new_acc = {'data':{'bid':args.add_account[0],'acc_num':args.add_account[1]},'type':'card'}
                payments.append(new_acc)
            elif args.remove:
                del payments[args.remove[0]-1]
            else:
                print("Index  |  Customer ID  | Payment")
                print(
                    "----------------------------------------------------------------------------")
                for i in range(len(rows[0][0])):
                    print("%5d   %7d          " % (i + 1, args.id), end="")
                    payment = rows[0][0][i]
                    if 'bid' in payment['data']:
                        print('bid = ' + str(payment['data']['bid']) + ', acc_num = ' + str(
                            payment['data']['acc_num']) + ", type = account")
                    else:
                        print('card_num = ' +
                              str(payment['data']['card_num']) + ", type = card")

            str_payments = json.dumps(payments)
            sql = "UPDATE customer SET payments = %(payments)s WHERE id = %(id)s;"
            cur.execute(sql, {
                "id": args.id,
                "payments": str_payments
            })
            conn.commit()

        elif args.function == "search":
            sql = "SELECT lat,lng FROM customer WHERE id = %(id)s;"
            cur.execute(sql,{"id":args.id})
            customer_loc = cur.fetchall()[0]

            is_all = args.a
            list_num = args.l[0]
            stores = []

            if args.o == 2:
                sql = "SELECT * FROM store;"
                cur.execute(sql)
                tmp_stores = cur.fetchall()
                print("Wait a second")
                for tmp_store in tmp_stores:
                    store_loc = (tmp_store[3],tmp_store[4])
                    distance = geodesic(customer_loc,store_loc)
                    store = list(tmp_store)
                    store.append(distance)
                    stores.append(store)
                stores = sorted(stores,key=lambda t: t[8])
                stores = stores[:list_num]
            else:
                if args.o[0] == 0:
                    sql = "SELECT * FROM store ORDER BY sname LIMIT %(list_num)s;"
                elif args.o[0] == 1:
                    sql = "SELECT * FROM store ORDER BY address LIMIT %(list_num)s;"
                else:
                    print("Invalid")
                    return

                cur.execute(sql,{"list_num":list_num})
                stores = cur.fetchall()

            # print(len(stores))
            # for store in stores:
            #     print(store)
            print("Sid  |  Sname   |  Address                                                | Open/closed")
            print("---------------------------------------------------------------------------------------")
            for store in stores:
                schedule = store[6]

                now_time = datetime.datetime.now()
                day = now_time.weekday()
                hour = str(now_time.time().hour)
                time = str(now_time.time().minute)
                if len(time)<2:
                    time = "0"+time
                time = hour+time
                is_open = False
                
                ## 가게의 영업 여부를 확인한다.
                if not schedule[day]['holiday']:
                    open_time = schedule[day]['open']
                    closed_time = schedule[day]['closed']
                    if open_time<=closed_time:
                        if open_time<=time and time<=closed_time:
                            is_open = True
                    # 24시간 영업으로 간주할 경우
                    else:
                        is_open = True
                    ## time이 24:30과 같은 invalid 한 값을 가지면 24시간 영업으로 간주
                    if open_time>'2400' or closed_time>'2400':
                        is_open = True
                if not is_all and not is_open:
                    continue
                print("%-5d %-10s %-45s"%(store[0],store[2],store[1]),end="")
                if is_open:
                    print("open")
                else:
                    print("closed")

        elif args.function == "store":
            sql = "UPDATE customer SET cart = %(cart)s WHERE id = %(id)s"
            str_cart = '{"sid":'+str(args.sid)+', "menus":[]}'

            cur.execute(sql, {
                "id": args.id,
                "cart": str_cart
            })

            conn.commit()
        elif args.function == "cart":
            sql = 'SELECT * FROM customer WHERE id = %(id)s'
            cur.execute(sql,{"id":args.id})
            rows = cur.fetchall()
            customer = rows[0]

            cart = customer[10]
            if not cart:
                print('There is no selected store')
                return
            sid = cart['sid']
            sql ='SELECT * FROM MENU WHERE sid=%(sid)s ORDER BY id;'
            cur.execute(sql,{"sid":sid})
            menus=cur.fetchall()

            if args.c:
                if len(args.c)%2==1:
                    print("Args Error: Creating cart need two values: menu_id, menu_count")
                    return
                str_cart = json.dumps(cart)
                selected_menu = menus[args.c[0]-1]

                cart['menus'].append({'mid':selected_menu[0],'menu_name':selected_menu[1],'menu_count':args.c[1]})
                str_cart = json.dumps(cart)

                sql = "UPDATE customer SET cart = %(cart)s WHERE id = %(id)s;"
                cur.execute(sql,{
                    "id":args.id,
                    "cart":str_cart
                })
            elif args.l:
                for i in range(len(cart['menus'])):
                    print(str(i+1)+". "+cart['menus'][i]['menu_name']+", count:"+str(cart['menus'][i]['menu_count']))
            elif args.r:
                del cart['menus'][args.r-1]
                str_cart = json.dumps(cart)
                sql = "UPDATE customer SET cart = null WHERE id = %(id)s;"
                cur.execute(sql,{"id":args.id})
                print("Remove is complete")
            elif args.p:
                cart_menus = cart['menus']
                order_time = datetime.datetime.now()
                
                for menu in cart_menus:
                    sql ="INSERT INTO orders (cid,sid,mid,menu_name,menu_count,order_time,status,payment,cphone) "
                    value_sql = "VALUES(%(cid)s,%(sid)s,%(mid)s,%(menu_name)s,%(menu_count)s,%(order_time)s,0,%(payment)s,%(cphone)s);"
                    sql = sql + value_sql
                    cur.execute(sql,{
                        "cid":args.id,
                        "sid":sid,
                        "mid":menu['mid'],
                        "menu_name":menu['menu_name'],
                        "menu_count":menu['menu_count'],
                        "order_time":datetime.datetime.now(),
                        "payment":json.dumps(customer[6][args.p[0]]),
                        "cphone":customer[2]
                    })
                conn.commit()
                sql = "UPDATE customer SET cart = null WHERE id = %(id)s;"
                cur.execute(sql,{"id":args.id}) 
                print("Payment is complete")
            else:
                print("Menu of Store",sid)
                print("--------------------------------")
                for i in range(len(menus)):
                    print(str(i+1)+". "+menus[i][1])
                print("--------------------------------")
            conn.commit()
        elif args.function == "list":
            if args.wating:
                sql = "SELECT * FROM orders WHERE cid = %(id)s AND status = 1;"
            else:
                sql = "SELECT * FROM orders WHERE cid = %(id)s;"
            cur.execute(sql,{"id":args.id})
            rows = cur.fetchall()
            print("Store name  |     Order time       |  Delivery status")
            for order in rows:
                sid = order[2]
                sql = "SELECT sname FROM store WHERE id = %(id)s;"
                cur.execute(sql,{"id":sid})

                result = cur.fetchall()
                sname = result[0][0]
                if order[9]==0:
                    status = "pending"
                elif order[9]==1:
                    status = "delivering"
                if order[9]==2:
                    status = "delivered"
                print("%-11s"%sname,end=" ")
                print(order[7].replace(microsecond = 0)," ",status)
    except Exception as err:
        err = "Invalid Input"
        print(err)
    pass


if __name__ == "__main__":
    start = time.time()
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(help='Command of Function')

    parser_info = subparsers.add_parser('info', help='Info of Customer')
    parser_info.add_argument('function', action='store_const', const='info', help='Funtion of Command')
    parser_info.add_argument('id', type=int, help='ID of Customer')

    parser_address = subparsers.add_parser('address', help='Addresses of Customer')
    parser_address.add_argument('function', action='store_const', const='address', help='Funtion of Command')
    parser_address.add_argument('id', type=int, help='ID of Customer')
    parser_address.add_argument("-c", "--create", nargs=1, help="Create New Address. Option of Address Fuction")
    parser_address.add_argument("-e", "--edit", nargs=2, help="Edit Addresses. Option of Address Fuction")
    parser_address.add_argument("-r", "--remove", nargs=1,type=int, help="Remove Address. Option of Address Fuction")

    parser_pay = subparsers.add_parser('pay', help='Payment of Customer')
    parser_pay.add_argument('function', action='store_const',const='pay', help='Funtion of Command')
    parser_pay.add_argument('id', type=int, help='ID of Customer')
    parser_pay.add_argument("--add-account", nargs=2, type = int, help="Add Account. Option of Pay Fuction")
    parser_pay.add_argument("--add-card", nargs=1, type = int,help="Add Card. Option of Pay Fuction")
    parser_pay.add_argument("-r", "--remove", nargs=1, type =int, help="Remove Payment. Option of Pay Fuction")

    parser_search = subparsers.add_parser('search', help='Search of Customer')
    parser_search.add_argument('function', action='store_const', const='search', help='Funtion of Command')
    parser_search.add_argument('id', type=int, help='ID of Customer')
    parser_search.add_argument('-a',action='store_true', help='Show All Store')
    parser_search.add_argument('-o',nargs=1, type=int, default = [0], help='Standard To Order')
    parser_search.add_argument('-l',nargs=1, type=int, default = [10],help='Number of Data To View')

    parser_store = subparsers.add_parser('store', help='Store of Customer')
    parser_store.add_argument('function', action='store_const', const='store', help='Funtion of Command')
    parser_store.add_argument('id', type=int, help='ID of Customer')
    parser_store.add_argument('sid', type=int, help='ID of Store')

    parser_cart = subparsers.add_parser('cart', help='Cart of Customer')
    parser_cart.add_argument('function', action='store_const', const='cart', help='Funtion of Command')
    parser_cart.add_argument('id', type=int, help='ID of Customer')
    parser_cart.add_argument('-c', nargs="*",type=int, help='Create a Cart')
    parser_cart.add_argument('-l', action='store_true', help='List of Cart')
    parser_cart.add_argument('-r', action='store_true', help='Remove a Cart')
    parser_cart.add_argument('-p', nargs=1,type=int, help='Make a Payment')

    parser_list = subparsers.add_parser('list', help="List of Customer's Orders")
    parser_list.add_argument('function', action='store_const', const='list', help='Funtion of Command')
    parser_list.add_argument('id', type=int, help='ID of Customer')
    parser_list.add_argument("-w","--wating", action="store_true", help='ID of Customer')


    args = parser.parse_args()
    # print(args)
    print("")
    main(args)
    print('')
    print("Running Time: ", end="")
    print(time.time() - start)
