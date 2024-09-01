from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from pyrogram.errors import ChatAdminRequired, UserNotParticipant, ChatWriteForbidden
from ANNIEMUSIC import app

#--------------------------

MUST_JOIN = "+I3UkkracnpI5ZTk1"
#------------------------

@app.on_message(filters.incoming & filters.private, group=-1)
async def must_join_channel(app: Client, msg: Message):
    if not MUST_JOIN:
        return

    try:
        # Check if the user is a participant of the MUST_JOIN channel
        try:
            await app.get_chat_member(MUST_JOIN, msg.from_user.id)
        except UserNotParticipant:
            # Generate the link for the MUST_JOIN channel
            if MUST_JOIN.isalpha():
                link = "https://t.me/" + MUST_JOIN
            else:
                chat_info = await app.get_chat(MUST_JOIN)
                link = chat_info.invite_link

            # Send a message to the user prompting them to join the channel
            try:
                await msg.reply_photo(
                    photo="https://telegra.ph/file/dfde87c32f8951c6b7628.jpg",
                    caption=(
                        "According to my database, you haven't joined Support yet. "
                        "If you want to use me, please join Support and start interacting with me again!"
                    ),
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [InlineKeyboardButton("Join", url=link)],
                        ]
                    )
                )
                await msg.stop_propagation()
            except ChatWriteForbidden:
                pass

    except ChatAdminRequired:
        print(f"Promote me as an admin in the must_join chat: {MUST_JOIN}!")

