import streamlit as st
import pandas as pd
import time
import os

# Create a folder called data in the main project folder
DATA_FOLDER = "data"
if not os.path.exists(DATA_FOLDER):
    os.makedirs(DATA_FOLDER)

# Define CSV file paths for each part of the usability testing
CONSENT_CSV = os.path.join(DATA_FOLDER, "consent_data.csv")
DEMOGRAPHIC_CSV = os.path.join(DATA_FOLDER, "demographic_data.csv")
TASK_CSV = os.path.join(DATA_FOLDER, "task_data.csv")
EXIT_CSV = os.path.join(DATA_FOLDER, "exit_data.csv")


def save_to_csv(data_dict, csv_file):
    # Convert dict to DataFrame with a single row
    df_new = pd.DataFrame([data_dict])
    if not os.path.isfile(csv_file):
        # If CSV doesn't exist, write with headers
        df_new.to_csv(csv_file, mode='w', header=True, index=False)
    else:
        # Else, we need to append without writing the header!
        df_new.to_csv(csv_file, mode='a', header=False, index=False)


def load_from_csv(csv_file):
    if os.path.isfile(csv_file):
        return pd.read_csv(csv_file)
    else:
        return pd.DataFrame()


def main():
    st.title("Panthers on the Run: Usability Test")

    home, consent, demographics, tasks, exit_tab, report = st.tabs(["Home", "Consent", "Demographics", "Task", "Exit Questionnaire", "Report"])
    
    with home:
        st.header("Welcome, Panther!")
        st.write("""
        Thanks for helping us test Panthers on the Run, a running tracker built for FIU runners.

        Here's how the test works:
        1. Sign the consent form (it's quick, like you!).
        2. Tell us a little about yourself and your running.
        3. Try out a task in the tracker while we take notes.
        4. Let us know how it went.
        5. Check out the results report.

        No pressure, as we want to help our panthers running community. Let's go!
        """)


    with consent:
        st.header("Consent Form")
        st.write("""
        Before we start, here's the deal:
        - An observer will take notes while you try out Panthers on the Run.
        - We'll track each run you log during the test.
        - The data we collect is only used for this class project.
        - There's no minimum required (distance or time). Every run counts!
        - You can stop at any time, no hard feelings.
        """)

        consent_given = st.checkbox("I agree to take part in this usability test")

        if st.button("Submit Consent"):
            if not consent_given:
                st.error("You need to check the box before we can start.")
            else:
                data_dict = {
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "consent_given": consent_given
                }
                save_to_csv(data_dict, CONSENT_CSV)
                st.success("Thanks! You're good to go. Head to the next tab.")

    with demographics:
        st.header("Demographic Questionnaire")

        with st.form("demographic_form"):
            name = st.text_input("What's your name? (optional, leave blank to stay anonymous)")
            age = st.number_input("How old are you?", min_value=10, max_value=100, value=20)
            occupation = st.text_input("What's your major or occupation?")
            run_frequency = st.selectbox(
                "How often do you run?",
                ["Never", "A few times a month", "Weekly", "A few times a week", "Daily"]
            )
            familiarity = st.multiselect(
                "Which running apps or watches have you used before?",
                ["Strava", "Coros", "Garmin", "Apple Watch", "Nike Run Club", "Other", "None"]
            )
            other_app = st.text_input("If you picked Other, which app or watch?")

            submitted = st.form_submit_button("Submit Demographics")
            if submitted:
                if name.strip() == "":
                    name = "Anonymous"

                apps_used = list(familiarity)
                if "Other" in apps_used and other_app.strip() != "":
                    apps_used.remove("Other")
                    apps_used.append(other_app.strip())

                data_dict = {
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "name": name,
                    "age": age,
                    "occupation": occupation,
                    "run_frequency": run_frequency,
                    "familiarity": ", ".join(apps_used)
                }
                save_to_csv(data_dict, DEMOGRAPHIC_CSV)

                confirmation_message = st.empty()
                confirmation_message.success("Got it, thanks! On to the task.")
                time.sleep(2)
                confirmation_message.empty()

    with tasks:
        st.header("Task Page")
        st.write(
                "Observers: pick a task, hit Start when the participant begins using Panthers on the Run, "
                "and hit Stop the moment they finish. The timer measures how long the task takes inside the app, "
                "not how long a run takes."
            )
        
        task_options = {
            "Task 1: Log a 5K run": "Add a new run with a distance of 5K and a time of your choice.",
            "Task 2: Set a weekly goal": "Set a mileage goal for the week, like running 10 miles.",
            "Task 3: View your weekly mileage": "Find the total miles you ran this past week."
        }

        selected_task = st.selectbox("Select Task", list(task_options.keys()))
        st.write("Task Description: " + task_options[selected_task])

        if st.button("Start Task Timer"):
            st.session_state["start_time"] = time.time()
            st.info("Timer started. Go, Panther, go!")

        if st.button("Stop Task Timer"):
            if "start_time" in st.session_state:
                task_duration = time.time() - st.session_state["start_time"]
                st.session_state["task_duration"] = task_duration
                st.info(f"Timer stopped: {task_duration:.1f} seconds")
            else:
                st.error("Start the timer first.")

        success = st.radio("Was the task completed successfully?", ["Yes", "No", "Partial"])
        observer_notes = st.text_area("Observer Notes")

        if st.button("Save Task Results"):
            duration_value = st.session_state.get("task_duration", None)

            data_dict = {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "task_name": selected_task,
                "success": success,
                "duration_seconds": round(duration_value, 1) if duration_value else "",
                "notes": observer_notes
            }
            save_to_csv(data_dict, TASK_CSV)

            if "start_time" in st.session_state:
                del st.session_state["start_time"]
            if "task_duration" in st.session_state:
                del st.session_state["task_duration"]

            confirmation_message = st.empty()
            confirmation_message.success("Task saved!")
            time.sleep(2)
            confirmation_message.empty()

    
    with exit_tab:
        st.header("Exit Questionnaire")
        st.write("Tell us how Panthers on the Run felt to use.")

        with st.form("exit_form"):
            satisfaction = st.slider(
                "Overall, how satisfied were you with the app? (1 = not at all, 5 = loved it)",
                min_value=1, max_value=5, value=3
            )
            difficulty = st.slider(
                "How difficult was it to complete the tasks? (1 = super easy, 5 = really hard)",
                min_value=1, max_value=5, value=3
            )
            would_use = st.slider(
                "How likely are you to use this app for your own runs? (1 = never, 5 = definitely)",
                min_value=1, max_value=5, value=3
            )
            liked_most = st.text_area("What did you like most about the app?")
            open_feedback = st.text_area("What would you change or add?")

            submitted_exit = st.form_submit_button("Submit Exit Questionnaire")
            if submitted_exit:
                data_dict = {
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "satisfaction": satisfaction,
                    "difficulty": difficulty,
                    "would_use": would_use,
                    "liked_most": liked_most,
                    "open_feedback": open_feedback
                }
                save_to_csv(data_dict, EXIT_CSV)

                confirmation_message = st.empty()
                confirmation_message.success("Thanks for the feedback fellow Panther!")
                time.sleep(2)
                confirmation_message.empty()

    with report:
        st.header("Usability Report - Aggregated Results")

        consent_df = load_from_csv(CONSENT_CSV)
        demographic_df = load_from_csv(DEMOGRAPHIC_CSV)
        task_df = load_from_csv(TASK_CSV)
        exit_df = load_from_csv(EXIT_CSV)

        # Summary numbers
        st.subheader("Quick Stats")
        col_participants, col_satisfaction, col_difficulty, col_would_use = st.columns(4)
        col_participants.metric("Participants", len(demographic_df))
        if not exit_df.empty:
            col_satisfaction.metric("Avg Satisfaction", f"{exit_df['satisfaction'].mean():.2f}")
            col_difficulty.metric("Avg Difficulty", f"{exit_df['difficulty'].mean():.2f}")
            col_would_use.metric("Avg Would Use", f"{exit_df['would_use'].mean():.2f}")

        # Task success by task
        st.subheader("Task Success")
        if not task_df.empty:
            success_counts = task_df.groupby(["task_name", "success"]).size().unstack(fill_value=0)
            st.bar_chart(success_counts, horizontal=True)
        else:
            st.info("No task data available yet.")

        # Average time per task
        st.subheader("Average Time Per Task (seconds)")
        if not task_df.empty:
            average_times = task_df.groupby("task_name")["duration_seconds"].mean()
            st.bar_chart(average_times, horizontal=True)
        else:
            st.info("No task data available yet.")

        # Exit questionnaire averages
        st.subheader("Exit Questionnaire Ratings")
        if not exit_df.empty:
            average_ratings = exit_df[["satisfaction", "difficulty", "would_use"]].mean()
            st.bar_chart(average_ratings, horizontal=True)
        else:
            st.info("No exit questionnaire data available yet.")

        # Running frequency of testers
        st.subheader("How Often Our Testers Run")
        if not demographic_df.empty:
            frequency_counts = demographic_df["run_frequency"].value_counts()
            st.bar_chart(frequency_counts, horizontal=True)
        else:
            st.info("No demographic data available yet.")

        # Raw data tables
        st.subheader("Raw Data")
        with st.expander("Consent Data"):
            st.dataframe(consent_df)
        with st.expander("Demographic Data"):
            st.dataframe(demographic_df)
        with st.expander("Task Performance Data"):
            st.dataframe(task_df)
        with st.expander("Exit Questionnaire Data"):
            st.dataframe(exit_df)

if __name__ == "__main__":
    main()