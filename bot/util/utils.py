import datetime


def build_form_blocks():
    return [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "次回の登校予定時刻を教えてください:cat2:"
            }
        },
        {
            "type": "input",
            "element": {
                "type": "datepicker",
                "initial_date": str(datetime.date.today() + datetime.timedelta(days=1)),
                "placeholder": {
                    "type": "plain_text",
                    "text": "Select a date",
                    "emoji": True
                },
                "action_id": "set-datepicker"
            },
            "label": {
                "type": "plain_text",
                "text": "日付",
                "emoji": True
            }
        },
        {
            "type": "input",
            "element": {
                "type": "timepicker",
                "initial_time": "08:00",
                "placeholder": {
                    "type": "plain_text",
                    "text": "Select time",
                    "emoji": True
                },
                "action_id": "set-timepicker"
            },
            "label": {
                "type": "plain_text",
                "text": "時間",
                "emoji": True
            }
        },
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "セット:cat:",
                        "emoji": True
                    },
                    "action_id": "set-school-time"
                }
            ]
        }
    ]


def convert_datetime_str_to_timestamp(date_str, time_str):
    tdatetime = datetime.datetime.strptime(
        f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
    return int(tdatetime.timestamp())
