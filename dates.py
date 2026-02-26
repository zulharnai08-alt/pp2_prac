from datetime import datetime, timedelta


def show_dates(): 
    today = datetime.now()
    yesterday = today - timedelta(days=1)
    tomorrow = today + timedelta(days=1)

    print("Today:     ", today.strftime("%Y-%m-%d"))
    print("Yesterday: ", yesterday.strftime("%Y-%m-%d"))
    print("Tomorrow:  ", tomorrow.strftime("%Y-%m-%d"))


if __name__ == "__main__":
    show_dates()
