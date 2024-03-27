import streamlit as st
from snowflake.snowpark.context import get_active_session
import matplotlib.pyplot as plt
from PIL import Image
import pandas as pd
import io
from datetime import datetime

# Function to create logo
def create_logo(text, font_size=20, font_weight='normal', font_family='sans-serif', font_color='black', bg_color='white'):
    """
    Function to create a logo image with specified text and styling parameters.

    Parameters:
    - text: The text to be displayed in the logo.
    - font_size: Font size of the text.
    - font_weight: Font weight of the text (e.g., 'normal', 'bold').
    - font_family: Font family of the text.
    - font_color: Color of the text.
    - bg_color: Background color of the logo.

    Returns:
    - Logo image buffer.
    """
    fig, ax = plt.subplots()
    ax.text(0.5, 0.5, text, ha='center', va='center', fontsize=font_size, fontweight=font_weight, fontfamily=font_family, color=font_color)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    ax.set_facecolor(bg_color)
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0, transparent=True)
    buf.seek(0)
    
    plt.close()
    
    return buf

# Get the current Snowflake session
session = get_active_session()

# Initialize session_state if not already initialized
if 'past' not in st.session_state:
    st.session_state.past = []
if 'generated' not in st.session_state:
    st.session_state.generated = []
if 'conversations' not in st.session_state:
    st.session_state.conversations = []

# Initialize session_id if not already initialized
if 'session_id' not in st.session_state:
    st.session_state.session_id = str(datetime.now().strftime("%Y%m%d%H%M%S"))

# Get user_name from st.experimental_user
user_name = st.experimental_user['user_name'] if 'user_name' in st.experimental_user else "Unknown User"

# st.write(user_name)

# Streamlit interface starts from here
st.success(
    """
    ***Welcome to SnowPeon, Your Virtual Assistant !👨‍🚀 ❄️***
    """
)

# Streamlit Sidebar
with st.sidebar.container():
    text = "KASMO"
    font_size = 100
    font_weight = "bold"
    font_family = "Times New Roman"
    font_color = "#3A77C7"
    bg_color = "#FFFFFF"
    
    logo_buffer = create_logo(text, font_size=font_size, font_weight=font_weight, font_family=font_family, font_color=font_color, bg_color=bg_color)
    st.image(Image.open(logo_buffer))
    st.markdown("-----")
    clear = st.sidebar.button("New Chat")
    view_history = st.sidebar.button("Chat History")

# If the 'New Chat' button is clicked, clear previous chats
if clear:
    st.session_state.past.clear()
    st.session_state.generated.clear()
    st.session_state.conversations.clear()

# Input text box for user questions
prompt = st.chat_input("Enter your question here")

# Query formation and access the Lama2-7b chat model from Snowflake cortex 
quest_q = f'''
select snowflake.cortex.complete(
        'llama2-70b-chat', 
        concat( 
            'Answer the question based on the context do not answer outside question of the context. You are a bot named SnowPeon only to help with insurance and policy documents, first greetings to user with your introduction, do not make answer if questions are not from context.
    Be concise,','Context: ', 
            (
                select CHUNK from CHATBOT.DATA_PROCESSING.PRIVATECAR_CHUNKS_VECTOR
                order by CHATBOT.DATA_PROCESSING.EUCLIDEAN_DISTANCE(
                CHATBOT.DATA_PROCESSING.QUERY_EMBED(
                '{prompt}'
                ), EMB
                ) limit 1
            ),
            'Question: ', 
            '{prompt}',
            'Current user',
            'Answer: '
        )
    ) as response;
'''

# Display response and append the chat from the previous session
if prompt:
    df_query = session.sql(quest_q).to_pandas()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state.past.append((prompt, timestamp))
    st.session_state.generated.append((df_query['RESPONSE'][0], timestamp))
    st.session_state.conversations.append((prompt, df_query['RESPONSE'][0], timestamp))

    conversation_df = pd.DataFrame(st.session_state.conversations, columns=['Question', 'Answer', 'Timestamp'])
    # st.write(conversation_df)
    session.sql("CREATE TABLE IF NOT EXISTS chat_history_new (Session_ID STRING, User_Name STRING, Question STRING, Answer STRING, Timestamp TIMESTAMP)").collect()
    
    insert_sql = "INSERT INTO chat_history_new (Session_ID, User_Name, Question, Answer, Timestamp) VALUES (?, ?, ?, ?, ?)"
    for index, row in conversation_df.iterrows():
        session.sql(insert_sql, (st.session_state.session_id, user_name, row['Question'], row['Answer'], row['Timestamp'])).collect()

st.markdown("____")

# if len(st.session_state.conversations) > 5:
#     st.session_state.conversations = st.session_state.conversations[-5:]

for i, (prompt, response, timestamp) in enumerate(st.session_state.conversations):
    st.warning(f"👤 {prompt}")
    st.info(f"🤖 {response}")

if view_history:
    st.subheader("Chat History")
    # Check if the user has the 'accountadmin' role

    current_role = session.get_current_role()
    # st.write("#######", current_role)
    if current_role == '"ACCOUNTADMIN"':
        # Users with 'accountadmin' role can see Session_ID
        chat_history_df = session.sql("SELECT * FROM chat_history_new").to_pandas()
    else:
        # Non-admin users can only see their own User_Name
        chat_history_df = session.sql("SELECT User_Name, Question, Answer, Timestamp FROM chat_history_new WHERE User_Name = ?",
                                       (user_name,)).to_pandas()
    st.dataframe(chat_history_df)
