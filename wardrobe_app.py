import streamlit as st
import sqlite3
from streamlit_free_text_select import st_free_text_select
import time

# --- DATABASE SETUP ---
conn = sqlite3.connect("wardrobe.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS wardrobe_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        type TEXT,
        color TEXT,
        vibe TEXT
    )
""")
conn.commit()

# --- Fetch distinct values from DB ---
cursor.execute("SELECT DISTINCT type FROM wardrobe_items where type <> ''")
type_options = [row[0] for row in cursor.fetchall()]
type_options = sorted(set(type_options + ["Top", "Bottom", "Dress", "Outerwear", "Shoes", "Accessory"]))

cursor.execute("SELECT DISTINCT color FROM wardrobe_items")
colour_options = [row[0] for row in cursor.fetchall()]
colour_options = sorted(set([c.capitalize() for c in colour_options]))

cursor.execute("SELECT DISTINCT vibe FROM wardrobe_items where vibe <> ''")
vibe_options = [row[0] for row in cursor.fetchall()]
vibe_options = sorted(set(vibe_options + ["Romantic", "Minimalist", "Edgy", "Bohemian", "Casual", "Formal"]))


# https://github.com/hummerichsander/streamlit-free-text-select
st.title("👗 My Virtual Wardrobe")

# --- Clear form after submission ---
if st.session_state.get("form_submitted"):
    st.session_state["add_name"] = ""
    st.session_state["add_color"] = ""
    st.session_state["add_vibe"] = ""
    st.session_state["add_type"] = ""
    st.session_state["form_submitted"] = False

# --- ADD NEW ITEM FORM ---
with st.form("add_item"):
    st.subheader("➕ Add New Item")
    name = st.text_input("Item name", key="add_name")
    # type_ = st.selectbox("Type", ["Top", "Bottom", "Dress", "Outerwear", "Shoes", "Accessory"], key="add_type")

    type_ = st_free_text_select(
        label="Type",
        options=type_options,
        index=None,
        placeholder="Select or enter a type",
        disabled=False,
        label_visibility="visible",
        key="add_type"
    )

    color = st_free_text_select(
        label="Color",
        options=colour_options,
        index=None,
        # format_func=lambda x: x.capitalize(),
        placeholder="Select or enter a colour",
        disabled=False,
        label_visibility="visible",
        key="add_color"
    )

    vibe = st_free_text_select(
        label="Vibe",
        options=vibe_options,
        index=None,
        placeholder="Select or enter a vibe",
        disabled=False,
        label_visibility="visible",
        key="add_vibe"
    )

    submit = st.form_submit_button("Add")

    if submit and st.session_state.add_name:
        cursor.execute("""
            INSERT INTO wardrobe_items (name, type, color, vibe)
            VALUES (?, ?, ?, ?)
        """, (st.session_state.add_name, st.session_state.add_type,
              st.session_state.add_color, st.session_state.add_vibe))
        conn.commit()
        st.success(f"Added: {st.session_state.add_name}")

        st.session_state["form_submitted"] = True
        time.sleep(2)
        st.rerun()

# --- LOAD ITEMS FROM DB ---
cursor.execute("SELECT id, name, type, color, vibe FROM wardrobe_items")
items = cursor.fetchall()

st.subheader("🧺 My Items")

for item in items:
    item_id, name, type_, color, vibe = item

    with st.expander(f"👚 {name} ({type_})"):
        st.markdown(f"**Color**: {color}  \n**Vibe**: {vibe}")

        # --- EDIT FORM ---
        with st.form(f"edit_form_{item_id}"):
            new_name = st.text_input("Name", value=name, key=f"name_{item_id}")
            new_type = st.text_input("Type", value=type_, key=f"type_{item_id}")
            new_color = st.text_input("Color", value=color, key=f"color_{item_id}")
            new_vibe = st.text_input("Vibe", value=vibe, key=f"vibe_{item_id}")

            col1, col2 = st.columns(2)
            if col1.form_submit_button("💾 Save Changes"):
                cursor.execute("""
                    UPDATE wardrobe_items
                    SET name = ?, type = ?, color = ?, vibe = ?
                    WHERE id = ?
                """, (new_name, new_type, new_color, new_vibe, item_id))
                conn.commit()
                st.success("Item updated. Please refresh to see changes.")
                st.rerun()  # Optional: uncomment to auto-refresh

            if col2.form_submit_button("🗑️ Delete"):
                cursor.execute("DELETE FROM wardrobe_items WHERE id = ?", (item_id,))
                conn.commit()
                st.warning("Item deleted. Please refresh to see changes.")
                st.rerun()  # Optional: uncomment to auto-refresh
