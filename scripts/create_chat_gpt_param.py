import json


def system_message_generator():
    """
    Generates a system message for defining the assistant's role.
    """
    return (
        "あなたはweb記事を作成する部門の担当者です。記事の分類分けを得意としています。"
    )


def temperature_generator(context):
    """
    Generates the temperature value based on the provided context.

    Args:
        context (str): Context for generating the temperature ("creative", "precise", etc.).

    Returns:
        float: A temperature value for controlling randomness in the GPT response.
    """
    if context == "creative":
        return 0.9
    elif context == "precise":
        return 0.3
    return 0.7


def edit_user_input(tag_data, entry):
    return (
        "記事のタイトルと内容を渡します。タグデータを渡すので、内容に適したタグを三つ選択してください。"
        "当てはまる内容が三つ以下の場合は、三つ以下で構いません。一つも当てはまらない場合はその他で返してください"
        "レスポンスの形式は配列形式で返してください。[タグ１,タグ2]のようにです。他の文言は不要です。"
        "タグデータは{}です。記事のタイトルは{}です。記事の内容は{}です".format(
            tag_data, entry["title"], entry["description"]
        )
    )
