import argparse
import requests


def parse_args():
    ap = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    ap.add_argument("--ip", required=True, type=str, help="Ip of server for which request is sent.")
    args = ap.parse_args()
    return args


def parse_market_order():
    print("Id: ")
    id = str(input())
    print("Name: ")
    name = str(input())
    print("Side: ")
    side = str(input())
    print("Quantity: ")
    quantity = int(input())

    return {"id": id, "name": name, "side": side, "quantity": quantity}


def parse_limit_order():
    print("Id: ")
    id = str(input())
    print("Name: ")
    name = str(input())
    print("Side: ")
    side = str(input())
    print("Quantity: ")
    quantity = int(input())
    print("Price: ")
    price = int(input())

    return {"id": id, "name": name, "side": side, "quantity": quantity, "price": price}


def parse_cancel_order():
    print("Id: ")
    id = str(input())
    print("Name: ")
    name = str(input())

    return {"id": id, "name": name,}


def main():
    args = parse_args()
    ip_address = args.ip

    print("Choose order type:")
    print("1 - market order")
    print("2 - limit order")
    print("3 - cancel order")

    order_type = int(input())

    if order_type == 1:
        message = parse_market_order()
        url_content = "market_order"
    elif order_type == 2:
        message = parse_limit_order()
        url_content = "limit_order"
    elif order_type == 3:
        message = parse_cancel_order()
        url_content = "cancel_order"
    else:
        raise ValueError("Wrong order type")

    request_address = ip_address + url_content

    if order_type == 4:
        response = requests.get(request_address)
    else:
        response = requests.post(request_address, json=message)
    print(response.json())


if __name__ == "__main__":
    main()
