import pandas as pd
import streamlit as st
import json
import requests

x_api_key = "pTguMzPJhjzS95wEkgEuPEpCXHkLxrPe"
token = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1aWQiOiI2YjliODBkMC0yNDMyLTExZWItYjI2NS0zYjBiYWNkOGE1ZjYiLCJpcCI6IjQ5LjI0OS42OS4yMiwgMTMwLjE3Ni4xODguMjMxIiwiY291bnRyeSI6IklOIiwiaWF0IjoxNjY2MTYwMDMwLCJleHAiOjE2NjY3NjQ4MzAsImF1ZCI6ImxlYXJuYXBwIiwiaXNzIjoiaHlkcmE6MC4wLjEifQ.gAyIL9Sd6jqLP36-AKOHVuaGRUuS4UBZPbokChT9mOA"

payload = {}
headers = {
    "x-api-key": x_api_key,
    "Authorization": token,
    "Content-Type": "application/json",
}

# get the list of all question sets
def get_all_question_sets():

    response = requests.request(
        "GET",
        "https://socrates.dev.learnapp.co/kraken/question-sets",
        headers=headers,
        data={},
    )

    question_sets_json = json.loads(response.text)["items"]

    question_set_list = {}

    for i in question_sets_json:
        question_set_list[i["title"]] = i["questionSetId"]

    return question_set_list


# get questions from a particular question set
def get_questions_from_set(view_question_set):

    view_question_set_id = get_all_question_sets()[view_question_set]
    response = requests.request(
        "GET",
        "https://socrates.dev.learnapp.co/kraken/question-sets/" + view_question_set_id,
        headers=headers,
        data={},
    )
    data = json.loads(response.text)["questions"]
    df = pd.DataFrame(data)

    return df


# create a new question set
def create_question_set(title):

    response = requests.request(
        "POST",
        "https://socrates.dev.learnapp.co/kraken/question-sets",
        headers=headers,
        data=json.dumps({"title": title}),
    )

    question_set_id = json.loads(response.text)


# create a new question
def create_question(payload):

    response = requests.request(
        "POST",
        "https://socrates.dev.learnapp.co/kraken/questions",
        headers=headers,
        data=payload,
    )
    questionId = json.loads(response.text)["questionId"]

    return questionId


# add a question to the question set
def add_question_to_set(questionSetId, questionId):
    url = (
        "https://socrates.dev.learnapp.co/kraken/question-sets/{}/questions/{}".format(
            questionSetId, questionId
        )
    )
    payload = json.dumps({"position": 1})
    response = requests.request("PUT", url, headers=headers, data=payload)


# delete a question set
def delete_question_set(questionSetDeleteId):

    response = requests.request(
        "DELETE",
        "https://socrates.dev.learnapp.co/kraken/question-sets/" + questionSetDeleteId,
        headers=headers,
        data={},
    )


# remove a question from a question set
def remove_question_from_set(questionSetRemoveId, questionRemoveId):

    url = (
        "https://socrates.dev.learnapp.co/kraken/question-sets/{}/questions/{}".format(
            questionSetRemoveId, questionRemoveId
        )
    )
    response = requests.request("DELETE", url, headers=headers, data={})


# UI for creating a new question set and adding question
with st.sidebar:
    # UI for creating a new question set
    st.subheader("Add a new Question Set")

    question_set_title = st.text_input("Enter the title of your Question Set", key=19)
    if st.button("Add Question Set"):
        create_question_set(question_set_title)
        st.experimental_rerun()

    st.write("----------")

    # UI for deleting a question set
    st.subheader("Delete a Question Set")
    question_set_delete = st.selectbox(
        "Select the Question Set",
        get_all_question_sets().keys(),
        key=29,
    )
    questionSetDeleteId = get_all_question_sets()[question_set_delete]

    if st.button("Delete Question Set"):
        delete_question_set(questionSetDeleteId)
        st.experimental_rerun()

    st.write("----------")

    # UI for adding a new question
    st.subheader("Add a question to a Question Set")
    question_set_add = st.selectbox(
        "Select question set", get_all_question_sets().keys(), key=39
    )
    questionSetId = get_all_question_sets()[question_set_add]

    questionType = st.selectbox(
        "Select question type",
        options=["MCQ_IMAGE", "MCQ_TEXT_OR_NUMBER", "SUBJECTIVE"],
    )
    answerType = st.selectbox(
        "Select answer type",
        options=["RANGE", "EXACT_VALUE", "SEQUENCE", "MULTIPLE_OPTIONS"],
    )
    optionType = st.selectbox(
        "Select answer type",
        options=["TEXT", "NUMBER", "IMAGE"],
    )
    question = st.text_input("Enter your question (in text)")
    timeLimit = st.select_slider(
        "Enter time limit (in secs)", options=[15, 30, 45, 60, 75, 90, 120]
    )
    difficulty = st.selectbox(
        "Select question difficulty",
        options=["easy", "medium", "difficult"],
    )

    total_options = st.select_slider(
        "Enter total options for this question", options=[2, 3, 4]
    )

    options = []
    for i in range(total_options):
        options_data = {}
        options_data["value"] = st.text_input("Enter the Option (in text)", key=i)
        options_data["isAnswer"] = st.selectbox(
            "Is this the correct answer?", options=[True, False], key=i + 5
        )
        options.append(options_data)

    # Create a question inside that particular question set
    if st.button("Add Question"):

        # Create a question
        payload = json.dumps(
            {
                "questionType": questionType,
                "answerType": answerType,
                "optionType": optionType,
                "difficulty": difficulty,
                "question": question,
                "timeLimit": timeLimit,
                "options": options,
            }
        )

        questionId = create_question(payload)

        # Add the question to the respective question set
        add_question_to_set(questionSetId, questionId)
        st.success("Your Question has been Added!")

    st.write("----------")

    # UI for removing a question from the question set
    st.header("Remove a question from the question set")
    question_set_remove = st.selectbox(
        "Select the Question Set", get_all_question_sets().keys(), key=49
    )
    questionSetRemoveId = get_all_question_sets()[question_set_remove]

    try:
        df_remove = get_questions_from_set(question_set_remove)
        df_remove.index += 1

        question_remove = st.selectbox(
            "Select the question no. to be removed",
            range(1, len(df_remove) + 1),
        )

        questionRemoveId = df_remove.iloc[int(question_remove) - 1]["questionId"]
        if st.button("Remove question from set"):
            remove_question_from_set(questionSetRemoveId, questionRemoveId)

    except:
        st.error("This question set has no questions")
    st.write("----------")

    #


# Title of the page (Main Page)
st.title("LearnApp Practice - Kraken")

# See the questions inside a questions set
try:
    view_question_set = st.selectbox(
        "Select the Question Set", get_all_question_sets().keys(), key=59
    )
    if st.button("Get Questions"):
        df = get_questions_from_set(view_question_set)
        df.index += 1

        df["allOptions"] = df["options"].apply(lambda x: [i.get("value") for i in x])
        df["correctOptions"] = df["options"].apply(
            lambda x: [i.get("value") for i in x if i["isAnswer"] == True]
        )

        st.dataframe(
            df[
                [
                    "questionType",
                    "answerType",
                    "optionType",
                    "question",
                    "timeLimit",
                    "difficulty",
                    "allOptions",
                    "correctOptions",
                    "isReleased",
                ]
            ]
        )
        # st.write(df["options"].apply(lambda x: [i.get("value") for i in x]))

except:

    try:
        if len(df) == 0:
            st.dataframe(df)
            st.error("There are no questions in this Question Set")
    except:
        st.error("Please reload the page")
        if st.button("Reload"):
            st.experimental_rerun()
