import streamlit as st
import pandas
import json
from io import StringIO

# 1. Method  and constant definitions
# ####################################

# Establish a hard-coded list that model stat and weapon dataframes will use for 
# columns
MODEL_STAT_COLUMNS = ["Model Name", "Move", "Toughness", "Save", "Invuln", "Wounds", "Leadership", "OC"]
WEAPON_STAT_COLUMNS = ["Selectable","Name", "Keywords" ,"Range", "Attacks", "Skill", "Strength", "AP", "Damage"]
UNIT_TYPE_LIST = ["Epic Hero", "Character", "Vehicle", "Monster", "Mounted", "Infantry", "Beast"]
# Establish a list of factions that the user can choose from
FACTION_LIST = ["Adepta Sororita", "Adeptus Custodes", "Adeptus Mechanicus", "Agents of the Imperium", "Astra Militarum",
                "Grey Knights", "Imperial Knights", "Space Marines", "Chaos Daemons", "Chaos Knights", "Chaos Space Marines",
                "Death Guard", "Thousand Sons", "World Eaters", "Aeldari", "Drukhari", "Genestealer Cults", "Leagues of Votann",
                "Necrons", "Orks", "T'au Empire", "Tyranids"]


def reset_unit_data():
    st.session_state["unit_object"] = {
        "unit_name": "",
        "unit_type": "",
        "faction": "",
        "stats": [],
        "wargear": [],
        "abilities": {
            "faction": [],
            "core": [],
            "unit": [],
            "has_wargear": False,
            "wargear": [],
            "has_supreme": False,
            "supreme": {}
        },
        "has_wounded": False,
        "wounded_values": {},
        "unit_composition": "",
        "keywords": []
    }
    st.rerun()


def dict_to_json_string(dict_input):
    converted_string = json.dumps(dict_input)
    return converted_string


def json_string_to_dict(string_input):
    converted_json = json.loads(string_input)
    return converted_json


@st.experimental_dialog("Load Unit")
def import_json_from_file():
    st.write("Drag a JSON file into the box below to load it's unit data")
    uploaded_file = st.file_uploader("Choose a file")
    accept_btn = st.button("Accept")
    if accept_btn:
        if uploaded_file is not None:
            read_json_dict = json.load(uploaded_file)
            st.session_state["unit_object"] = read_json_dict
        st.rerun()


@st.experimental_dialog("Save Unit")
def export_json_to_file():
    st.write("Click the button below to download your JSON file")
    json_output = json.dumps(st.session_state["unit_object"])
    download_btn = st.download_button(
        "Download", 
        data=json_output,
        file_name="" + st.session_state["unit_object"]["unit_name"] + ".json",
        mime="application/json")
    if download_btn:
        st.rerun()


def set_type_index():
    if st.session_state["unit_object"]["unit_type"] == "":
        return None
    else:
        faction_index = UNIT_TYPE_LIST.index(st.session_state["unit_object"]["unit_type"])
        return faction_index


def set_faction_index():
    if st.session_state["unit_object"]["faction"] == "":
        return None
    else:
        faction_index = FACTION_LIST.index(st.session_state["unit_object"]["faction"])
        return faction_index


# Split a list at every comma, retun a list
def string_to_list(string_input):
    converted_list = string_input.split(",")
    return converted_list


# Join a list together as a single string
def list_to_string(list_input):
    converted_string = ",".join(list_input)
    return converted_string


# Fetch stats from the 'supreme' dict within abilities
def fetch_supreme_stat(stat_key):
    tested_value = st.session_state["unit_object"]["abilities"]["supreme"].get(stat_key, None)
    if  tested_value != None:
        return st.session_state["unit_object"]["abilities"]["supreme"][stat_key]
    else:
        return ""
    

def fetch_wounded_stat(stat_key):
    test_for_wounded_text = st.session_state["unit_object"]["wounded_values"].get(stat_key, None)
    if test_for_wounded_text != None:
        return st.session_state["unit_object"]["wounded_values"][stat_key]
    else:
        return ""


# 2. Streamlit layout
# #####################

# Establish the dict "unit_object" to work with, if it does not exist
if 'unit_object' not in st.session_state:
    reset_unit_data()


st.set_page_config(layout="wide")
title_block = st.title("CrusadeTome Unit Converter - Test Mode")
# Buttons for saving, loading and resetting the current data
button_block = st.container()
with button_block:
    new_col, load_col, save_col = st.columns(3)
    new_unit_btn = new_col.button("New Unit")
    if new_unit_btn:
        reset_unit_data()
    load_unit_btn = load_col.button("Load Unit")
    if load_unit_btn:
        import_json_from_file()
    save_unit_btn = save_col.button("Save Unit")
    if save_unit_btn:
        export_json_to_file()



# Start of 'data entry' block 
header_block = st.header("Data Entry", divider="violet")
with st.form("unit_form"):
    stat_col, ability_col = st.columns(2)
    with stat_col:
        unit_core_data_block = st.container(border=True)
        with unit_core_data_block:
            unit_name_input = st.text_input("Unit Name", st.session_state["unit_object"]["unit_name"])
            unit_type_selector = st.selectbox("Unit Type", UNIT_TYPE_LIST, index=set_type_index())
            unit_faction_selector = st.selectbox("Unit Faction", FACTION_LIST, index=set_faction_index())
        # Tool for inputting the stats of the unit, both for the 
        # individual models and for wargear. 
        unit_stat_block = st.container(border=True)
        with unit_stat_block:
            unit_stats_label = st.write("Model Stats")
            model_stat_frame = pandas.DataFrame(st.session_state["unit_object"]["stats"], columns=MODEL_STAT_COLUMNS)
            stat_editor = st.data_editor(
                model_stat_frame, 
                column_config= {
                    "Name": st.column_config.TextColumn(
                        "Model Name",
                        max_chars=64,
                    ),
                    "Move": st.column_config.NumberColumn(
                        "M",
                        help="Move",
                        min_value=1,
                        max_value=30,
                        step=1,
                        format="%d\""
                    ),
                    "Toughness": st.column_config.NumberColumn(
                        "T",
                        help="Toughness",
                        min_value=1,
                        max_value=14,
                        step=1
                    ),
                    "Save": st.column_config.NumberColumn(
                        "S",
                        help="Save",
                        min_value=1,
                        max_value=9,
                        step=1,
                        format="%d+"
                    ),
                    "Invuln": st.column_config.NumberColumn(
                        "Inv",
                        help="Invulnerable Save",
                        min_value=1,
                        max_value=9,
                        step=1,
                        format="%d+"
                    ),
                    "Wounds": st.column_config.NumberColumn(
                        "W",
                        help="Wounds",
                        min_value=1,
                        max_value=40,
                        step=1,
                    ),
                    "Leadership": st.column_config.NumberColumn(
                        "Ld",
                        help="Leadership",
                        min_value=1,
                        max_value=12,
                        step=1,
                        format="%d+"
                    ),
                    "OC": st.column_config.NumberColumn(
                        "OC",
                        help="Move",
                        min_value=1,
                        max_value=8,
                        step=1,
                    ),
                },
                use_container_width=True,
                num_rows="dynamic",
            )
        # End of unit_stat_block


        wargear_stat_block = st.container(border=True)
        with wargear_stat_block:
            unit_wargear_label = st.write("Unit Wargear")
            wargear_frame = pandas.DataFrame(st.session_state["unit_object"]["wargear"], columns=WEAPON_STAT_COLUMNS)
            wargear_editor = st.data_editor(
                wargear_frame,
                num_rows="dynamic",
                use_container_width=True,
                column_config= {
                    "Selectable": st.column_config.CheckboxColumn(
                        "Multi?",
                        help="Is this part of a multi-profile weapon",
                        default=False
                    ),
                    "Name": st.column_config.TextColumn(
                        "Weapon",
                        max_chars=64,
                    ),
                    "Keywords": st.column_config.TextColumn(
                        "Keywords",
                        help="Separate keywords with commas",
                        max_chars=80,
                    ),
                    "Range": st.column_config.TextColumn(
                        "Range",
                        help="Range should either be a number or 'Melee'",
                        max_chars=5
                    ),
                    "Attacks": st.column_config.NumberColumn(
                        "Attacks",
                        min_value=1,
                        max_value=20,
                        step=1
                    ),
                    "Skill": st.column_config.NumberColumn(
                        "Skill",
                        min_value=2,
                        max_value=6,
                        step=1,
                        format="%d+"
                    ),
                    "Strength": st.column_config.NumberColumn(
                        "Strength",
                        min_value=2,
                        max_value=30,
                        step=1
                    ),
                    "AP": st.column_config.NumberColumn(
                        "AP",
                        min_value=2,
                        max_value=30,
                        step=1,
                        format="-%d"
                    ),
                    "Damage": st.column_config.TextColumn(
                        "Damage",
                        help="either as a number or as a 'D(x)': example - D3",
                        max_chars=6
                    ),
                }
            )        
        # End of 'wargear_stat_block'


        unit_comp_area = st.text_area(
            "Unit Composition", 
            value=st.session_state["unit_object"]["unit_composition"]
        )


        keywords_input = st.text_input(
            "Keywords", 
            help="Separate keywords with commas ONLY",
            value=list_to_string(st.session_state["unit_object"]["keywords"]))
    # end of 'unit_col'


    with ability_col:
        # Section for core abilities, like 'Stealth' or 'Infiltrators'
        # Also for faction abilities like 'Oath of Moment'
        unit_ability_label = st.write("Unit Abilities")
        core_ability_input = st.text_input(
            "Core Abilities", 
            list_to_string(st.session_state["unit_object"]["abilities"]["core"])
        )
        faction_ability_input = st.text_input(
            "Faction Abilities",
            list_to_string(st.session_state["unit_object"]["abilities"]["faction"])
        )
        # Section for the individual unit's abilities
        ability_frame = pandas.DataFrame(st.session_state["unit_object"]["abilities"]["unit"], columns=["name", "text"])
        ability_editor = st.data_editor(
            ability_frame,
            key="ability_editor",
            num_rows="dynamic",
            use_container_width=True,
            column_config={
                "name": st.column_config.TextColumn(
                    "Ability Name",
                    max_chars=96
                ),
                "text": st.column_config.TextColumn(
                    "Text"
                )
            }
        )
        # Section with expandable fields for wargear and 'Supreme Commander' abilities
        with st.expander("Wargear Abilities"):
            wargear_ability_check = st.checkbox(
                "Does unit have wargear abilities?", 
                value=st.session_state["unit_object"]["abilities"]["has_wargear"]
            )

            wargear_ability_frame = pandas.DataFrame(st.session_state["unit_object"]["abilities"]["wargear"],columns=["name", "text"])

            wargear_ability_editor = st.data_editor(
                wargear_ability_frame,
                key="wargear_ability_editor",
                num_rows="dynamic",
                use_container_width=True,
                column_config={
                    "name": st.column_config.TextColumn(
                        "Name",
                        max_chars=96
                    ),
                    "text": st.column_config.TextColumn(
                        "Text"
                    )
                }
            )
        # End of Wargear Abilities


        with st.expander("'Supreme Commander' Abilities"):
            supreme_check = st.checkbox(
                "Does unit have Supreme Commander abilities?", 
                value=st.session_state["unit_object"]["abilities"]["has_supreme"]
            )
            
            supreme_name_input = st.text_input("Supreme Ability Name", fetch_supreme_stat("name"))
            supreme_core_input = st.text_area("Supreme Ability Core Text", fetch_supreme_stat("core"))
            left_col, middle_col, right_col = st.columns(3)
            with left_col:
                first_supreme_name = st.text_input("1st Ability Name", fetch_supreme_stat("first_name"))
                first_supreme_input = st.text_area("Ability Text", fetch_supreme_stat("first_text"), key="first_supreme_input")
            with middle_col:
                second_supreme_name = st.text_input("2nd Ability Name", fetch_supreme_stat("second_name"))
                second_supreme_input = st.text_area("Ability Text", fetch_supreme_stat("second_text"), key="second_supreme_input")
            with right_col:
                third_supreme_name = st.text_input("3rd Ability Name", fetch_supreme_stat("third_name"))
                third_supreme_input = st.text_area("Ability Text", fetch_supreme_stat("third_text"), key="third_supreme_input")
    # End of Supreme Abilities
        
        with st.expander("'Damaged' State"):
            wounded_check = st.checkbox(
                "Does unit have a 'Damaged' state?",
                value=st.session_state["unit_object"]["has_wounded"])
            wounded_threshold_input= st.text_input(
                "Wound Threshold",
                help="ex. '1-6 Wounds Remaining'",
                value=fetch_wounded_stat("threshold")
            )
            wounded_text_input = st.text_input(
                "Wounded Text",
                value=fetch_wounded_stat("text")
            )


    # Create submission button for form data. When form is submitted,
    # all data is written to the "unit_object" dict in session state.
    submit_unit_data = st.form_submit_button("Submit Unit Data")
    if submit_unit_data:
        st.session_state["unit_object"]["unit_name"] = unit_name_input
        st.session_state["unit_object"]["unit_type"] = unit_type_selector
        st.session_state["unit_object"]["faction"] = unit_faction_selector
        st.session_state["unit_object"]["stats"] = json.loads(stat_editor.to_json(orient="records"))
        st.session_state["unit_object"]["wargear"] = json.loads(wargear_editor.to_json(orient="records"))
        st.session_state["unit_object"]["unit_composition"] = unit_comp_area
        st.session_state["unit_object"]["keywords"] = string_to_list(keywords_input)
        st.session_state["unit_object"]["abilities"]["faction"] = string_to_list(faction_ability_input)
        st.session_state["unit_object"]["abilities"]["core"] = string_to_list(core_ability_input)
        st.session_state["unit_object"]["abilities"]["unit"] = json.loads(ability_editor.to_json(orient="records"))
        st.session_state["unit_object"]["abilities"]["has_wargear"] = wargear_ability_check
        if st.session_state["unit_object"]["abilities"]["has_wargear"] == True:
            st.session_state["unit_object"]["abilities"]["wargear"] = json.loads(wargear_ability_editor.to_json(orient="records"))
        st.session_state["unit_object"]["abilities"]["has_supreme"] = supreme_check
        if st.session_state["unit_object"]["abilities"]["has_supreme"] == True:
            st.session_state["unit_object"]["abilities"]["supreme"]["name"] = supreme_name_input
            st.session_state["unit_object"]["abilities"]["supreme"]["core"] = supreme_core_input
            st.session_state["unit_object"]["abilities"]["supreme"]["first_name"] = first_supreme_name
            st.session_state["unit_object"]["abilities"]["supreme"]["first_text"] = first_supreme_input
            st.session_state["unit_object"]["abilities"]["supreme"]["second_name"] = second_supreme_name
            st.session_state["unit_object"]["abilities"]["supreme"]["second_text"] = second_supreme_input
            st.session_state["unit_object"]["abilities"]["supreme"]["third_name"] = third_supreme_name
            st.session_state["unit_object"]["abilities"]["supreme"]["third_text"] = third_supreme_input
        st.session_state["unit_object"]["has_wounded"] = wounded_check
        if st.session_state["unit_object"]["has_wounded"] == True:
            st.session_state["unit_object"]["wounded_values"]["threshold"] = wounded_threshold_input
            st.session_state["unit_object"]["wounded_values"]["text"] = wounded_text_input


# TEST AREA
st.subheader("Unit Data Preview")
st.write("Please verify all data before saving!")
st.write(st.session_state["unit_object"])


# st.json(st.session_state["unit_object"])