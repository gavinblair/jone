import argparse

def convert_currency(amount, from_currency, to_currency):
    # Placeholder function. In a real-world application, you would need to integrate
    # with an API to get the current exchange rates.
    # This function currently just returns the same amount for demonstration.
    return amount * .75

def main():
    parser = argparse.ArgumentParser(description='Currency Conversion Tool')
    parser.add_argument('-a', '--amount', type=float, required=True, help='Amount to convert')
    parser.add_argument('-f', '--from_currency', type=str, required=True, help='Currency to convert from')
    parser.add_argument('-t', '--to_currency', type=str, required=True, help='Currency to convert to')

    args = parser.parse_args()

    converted_amount = convert_currency(args.amount, args.from_currency, args.to_currency)
    print(f"{args.amount} {args.from_currency} is {converted_amount} {args.to_currency}")

if __name__ == "__main__":
    main()
