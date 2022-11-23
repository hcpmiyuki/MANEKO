import os
import re
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import datetime
import logging

# ログレベルを DEBUG に変更
logging.basicConfig(level=logging.DEBUG)

app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

@app.message("hello")
def message_hello(message, say):
    say(f"呼んだ？ <@{message['user']}>:cat:")

# chatbotにメンションが付けられたときのハンドラ
@app.event("app_mention")
def respond_to_mention(client, body, context, logger, say):
    try:
        message = body["event"]["text"]
        # メッセージに「時間」が含まれていたら登校予定時刻を入力するフォームをSlackに送信する
        if "時間" in message:
            say(
                blocks=build_form_blocks()
            )
        # メッセージに「到着」が含まれていた場合の処理
        elif "到着" in message:
            # スケジュールされたメッセージを取得
            result = client.chat_scheduledMessages_list(
                channel=context["channel_id"],
            )
            scheduled_messages = result["scheduled_messages"]
            if len(scheduled_messages) > 0:
                # スケジュールされたメッセージを削除する
                for message in scheduled_messages:
                    client.chat_deleteScheduledMessage(
                        channel=context["channel_id"],
                        scheduled_message_id=message['id']
                    )
                say("おめでとうございます! 目標時刻に間に合いました!:cat:")
                return
            say("登校予定が登録されていません:cat:")
        else:
            say(f"呼んだ？ <@{context['user_id']}>:cat:")
    except Exception as e:
        say("処理に失敗しました:crying_cat_face:")
        logger.error(e)


@app.action("set-school-time")
def handle_set_school_time(client, ack, say, body, context, logger):
    ack()
    try:
        selected_date: str
        selected_time: str
        for form_state in body['state']['values'].values():
            if 'set-datepicker' in form_state and 'selected_date' in form_state['set-datepicker']:
                selected_date = form_state['set-datepicker']['selected_date']
            elif 'set-timepicker' in form_state and 'selected_time' in form_state['set-timepicker']:
                selected_time = form_state['set-timepicker']['selected_time']
            else:
                raise Exception("Unexpected action_id.")

        if selected_date == "": raise Exception("Failed to get selected_date.")

        if selected_time == "": raise Exception("Failed to get selected_time.")

        result_scheduled_messages = client.chat_scheduledMessages_list(
            channel=context["channel_id"],
        )

        if len(result_scheduled_messages["scheduled_messages"]) > 0:
            say("既に登校予定が登録されています:cat:")
            return

        client.chat_scheduleMessage(
            channel=context["channel_id"],
            text="登校予定時刻ですよ〜〜〜:anger::pouting_cat:",
            post_at=convert_datetime_str_to_timestamp(selected_date, selected_time)
        )

        say(f"{selected_date} {selected_time}にMANEKOをセットしました:cat:")
    except Exception as e:
        say("登校予定の登録に失敗しました:crying_cat_face:")
        logger.error(e)

@app.action("set-datepicker")
def handle_set_datepicker(ack):
    ack()


@app.action("set-timepicker")
def handle_set_timepicker(ack):
    ack()


@app.event("message")
def handle_message_events(body, logger):
    logger.info(body)


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


# アプリを起動します
if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()
