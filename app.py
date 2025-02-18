import streamlit as st
import io

from randomizer.randomizer.randomizer import Z1Randomizer

st.set_page_config(page_title="Zelda \"Re-Randomizer\"", layout="wide")
st.image("https://streamlit.io/images/brand/streamlit-mark-color.png", width=78)
st.write(
    """
    # Zelda One Item Randomizer 

    A simple open-source Zelda Randomizer by Tetra
    """
)
    
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    "Please upload a Legend of Zelda ROM.",
    accept_multiple_files=False,
    type=['nes'],
    help="Please upload a Legend of Zelda ROM",
)
if uploaded_file is None:
    st.info(
        "To continue, please upload a Legend of Zelda ROM file by dragging and dropping it in the widget above or by clicking the \"Browse Files\" button."
        )
    st.stop()

output_filename = uploaded_file.name[:-4] + '_zora.nes'
  
z1randomizer = Z1Randomizer()
z1randomizer.SettingsNew(uploaded_file, 1234)
  
patch = z1randomizer.GetPatch()
output_rom_data = io.BytesIO(uploaded_file.getvalue())
for address in patch.GetAddresses():
    output_rom_data.seek(address)
    output_rom_data.write(bytes(patch.GetData(address)))

st.download_button(
    label="Download randomized ROM file (%s)" % output_filename,
    data=output_rom_data,
    file_name=output_filename,
    mime="application/octet-stream",
) 


def junk():
  pass

  """def stuff():
    try:
        bytes_data = uploaded_file.getvalue()
        filename = uploaded_file.name
        match = re.search(r"[-_](\d+)_([A-Za-z0-9]+)\.nes", filename)
        assert match
        seed = int(match.group(1))
        flagstring = match.group(2)
        out_filename = filename.replace(f"_{flagstring}.nes", f"_{flagstring}_rerandomized.nes")
        code = "%s,  %s,  %s,  %s" % (ITEMS[bytes_data[0xAFD3]], ITEMS[bytes_data[0xAFD2]],
                                      ITEMS[bytes_data[0xAFD1]], ITEMS[bytes_data[0xAFD0]]) 
    except Exception as e:
      import logging
      logging.exception("!")
      st.info("Sorry, this ROM doesn't seem to be supported. Please try a different ROM.")
      st.stop()
  """

  #st.info(
  #     """
  #     #### Info for uploaded ROM:
  #     Filename: %s\n
  #     Seed: %d\n
  #     Flagset: %s\n
  #     Code: %s
  #     """
  # % (filename, seed, flagstring, code)
  # )
  
  """
  ITEMS = {
      0x00: "Bombs",
      0x01: "Wooden Sword",
      0x02: "White Sword",
      0x03: "No Item",
      0x04: "Bait",
      0x05: "Recorder",
      0x06: "Blue Candle",
      0x07: "Red Candle",
      0x08: "Wooden Arrow",
      0x09: "Silver Arrow",
      0x0A: "Bow",
      0x0B: "Magical Key",
      0x0C: "Raft",
      0x0D: "Ladder",
      0x0E: "Triforce",  # Big L9 triforce, not small tringle
      0x0F: "5 Rupees",
      0x10: "Wand",
      0x11: "Book",
      0x12: "Blue Ring",
      0x13: "Red Ring",
      0x14: "Power Bracelet",
      0x15: "Letter",
      0x16: "Compass",
      0x17: "Map",
      0x18: "1 Rupee",
      0x19: "Key",
      0x1A: "Heart Container",
      0x1B: "Triforce",
      0x1C: "Shield",
      0x1D: "Boomerang",
      0x1E: "Magical Boomerang",
      0x1F: "Blue Potion",
      0x21: "Clock", 
      0x22: "Heart",
      0x23: "Fairy",
      0x24: "?????",
      0x25: "??????",
      0x26: "???????",
      0x27: "Beam",
    
  }

  def parse_filename(filename):
    seed_pattern = r"_(\d+)"
    flags_pattern = r"_[A-Za-z0-9]+)\."
  """  
  