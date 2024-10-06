import asyncio
import json
import os

# List of default channels
DEFAULT_CHANNELS = [
    'actressbluelion', 'actress_malavika_mohanan', 'thunderthighhss', 'actress_gallery_hot', 
    'hot_actress_model_pics', 'actresshot76', 'hotreelsgirlsss', 'ActressUhdEdits', 
    'actresspanorama', 'ActressThanos', 'devilyyyyyy', 'actressphobia', 'Desi_Hot_Girls_Photos', 
    'onlyhotactress2', 'ActressUnfiltered', 'Actress_Photos_Videos', 'Shama_Sikanders', 
    'das_18', 'south_heroines_official', 'celebbcorner', 'photography_kerala', 
    'actresshot0', 'thedesiactress', 'bollywood_feverrr', 'Jacqueline_fernandez_Official', 
    'Ketika_Sharma_Official', 'Neha_Shetty_Official', 'hotactresstuff', 'DesiActress1', 
    'yashikaveriyan', 'tamilactress_in', 'actress_hot_stuffs', 'Amikathesexyitem', 
    'fcactressclub', 'sonikachandigarh22', 'avneet_kaurOfficial_nsp', 'kerala_gallery', 
    'Actresz_Paradise', 'Yajnaseni25', 'ActressoG', 'namrita_malla4', 'kanikamannsexy', 
    'malluactress_pics', 'official_aayushijaiswaal', 'nilanambiar_model', 
    'EsshanyaMaheshwari_Hot', 'Sofia_Ansaris', 'MeghaShukla_fc', 'namritamalla', 
    'rashikhanna1', 'UHD_Actress_Hd', 'Amikathesexyitem', 'Actress_Collection_India', 
    'Instagramreelshortiktokvideos', 'Tollywood_Heroines', 'KetikaSharma_Pooja_Bhalek', 
    'actressUHDpics_ksl', 'tamanna_bhatia_fans', 'actresgalery', 'jhanvi_Kapoor_fcs', 
    'Kajal_Aggarwal_Official', 'Esshanya_maheshwari', 'trendingbeauties69', 
    'poonam_aap', 'Anjaligaud_onlyfans', 'poonam_sassy_ps', 'poonambajwapics', 
    'Sofia_ansari23', 'Namratamalla_fc', 'ramyapandianpic', 'dipshikha_roynxy', 
    'surleen_officiall', 'sandalwooddy', 'kaursimrannn', 
    'SamanthaAkkineni_Official', 'RakulPreetSingh_Official', 
    'Rashi_Khanna_official', 'Pooja_Hegde_Official', 'actressadda98', 
    'actress_simran_kaur', 'Kriti_shettypics', 'nivetha_pethuraj_official', 
    'actress_gallery07', 'QHDPosts', 'hotreelsgirls', 'Saniya_Ayyappan', 
    'priyaballav_joinmyapp', 'esratesmita', 'hina_khan_official', 'DesiBongSundori', 
    'HansikaKrishna1', 'kiaraadvanilovely', 'aslimonal_fc', 
    'priyankabiswas_diviyakhan', 'gimaashilover', 'actressaddahot', 
    'temptingactress', 'AngelRaiPage', 'Anu_Emmanuel_official_fc', 
    'indian_actress_hd_Photos', 'katesharma_1907', 'aditi_ke_fans', 
    'hiral_radadiya_93', 'NidhhiAgerwal_Official', 'Bhumi_Pednekar_Official', 
    'southindianglamour', 'Dimple_Nxy', 'AnikhaSurendran_Official', 
    'pratikasood_fans', 'aanchalmunjalofficial', 'Simran_Official', 
    'Tamanna_bhatia_fcs', 'DivyaBharathi_Official', 'Vedhika_Kumar_Official', 
    'bengaliactres', 'vishnupriyabhimeneni_fc', 'Madonna_Sebastian_Official', 
    'Amikathesexyitemoftutionteacher', 'thunderrthighs', 'gimaashiofficial', 
    'Navelloverssss', 'ipoojabhalekar', 'Sreeleela_official', 
    'actresswallpapergalore', 'Meetii_kalher_app', 'Ayeshaa_Khan_Official_Pics', 
    'desidance143', 'alekhayharika', 'MeenakshiChaudharya', 
    'Rituvarmaa', 'anupamaparmeshwara', 'ivana_actress', 
    'ishwaryamenon', 'Reginacassandraa', 'kavya_thapar_a', 
    'nainaganguly', 'Celebrity_buzz', 'Prakritipavaniofficial', 
    'Iswarya_Menon', 'KrithiShetty_fc', 'KritiSanon_Official', 
    'Shraddha_Srinath', 'AnjuKurian_Official', 'actress_ai_images', 
    'Malavika_Mohanan_Official', 'sareebongs', 'sareebabes', 
    'pragyanagragoddess', 'Actress_Anime_Gallery', 'Tina_Nandi_all_webseries', 
    'SL_Actress_Gallery', 'Ashika_Ranganath_Official', 'EsmitaEsrat', 
    'beautydancemasti', 'Sadha_Official', 'urvashirautelaaa', 
    'Nivethapethurajja', 'realmishtibasuu', 'Vedhikakumarr', 
    'hotreels01', 'nehasingh007', 'Bhavana_Menon_Official', 
    'ishmenon', 'suhanakhanofficial', 'Shivangi_Joshi_official', 
    'anushka_sen', 'sre_leela', 'ashika_ranganath', 
    'Shanvi_Srivastava', 'oriyasarkar091', 'reelshotgirls', 
    'BengaliActressLover', 'shirleysetialover', 'AnkitaSharma_fan', 
    'Surabhi_Samriddhi_chinkiMinki', 'Urfijavedofficial', 
    'Ashnoor_kaurSexy', 'Donal_Bisht_hot', 'Pareksharana', 
    'ShivangiJoshi_Love', 'bikinigirls001', 'hotreels0', 
    'hotreelsinsta', 'hotreels3', 'Rhea_Chakraborty_nsp', 
    'yashikaaannand', 'Yashika_Aannand_Official', 'Safcl', 
    'malayalamActressGallery', 'jannat_jubair', 'mouni_roy_nsp', 
    'aakshitaagnihotri', 'awesomeghosham', 'yeshasagarworld', 
    'sharma_karishma', 'sofiaansari9991', 'aditi_budhathoki', 
    'actresspics80', 'SakshiAgarwal_Official', 'catherine_tresa_nsp', 
    'MEeoW_Web_Series_club', 'hottie_instagram_ns', 'nikitasharmaofficial', 
    'actress_world026', 'ruhanisharma1', 'roma_varadkar_official', 
    'ashikaranganathoffic', 'apoo_17', 'MeghaDasSlut', 
    'vansheenvv', 'DivaflawlessOF', 'fappy_actresses', 'hottie_in_dress',
    'KaamaGurusLust', 'renu_chandra_1', 'mysteriouszheaa', 'pheonixx_girl', 
    'duskybae_appexclusive', 'Duskybae_97', 'nidhi_moodybeasty', 
    'yoursudiipaa', 'stylewithplixxi_officialx', 'triyasharoy_official', 
    'dimplenyx_dipshikharoy', 'divaflawless', 'Prajakta_Dusane_GG', 
    'brishi_backup', 'ApoorvaArora7', 'PoonamBajwa1', 
    'RuhaniSharma_fc', 'bongsundori', 'shivangijoshi18', 
    'HOTT_GIRL_SARA_CAM', 'AhsaasChanna_0', 'magicollection3', 
    'hot_insta_reels_hotreels', 'kanika_mannfan', 'megha_shuklaoriginal', 
    'priyankajawalkarr', 'GaramTikTokGirls', 'mallu_Models_hub', 'shambhavirajput1997',
    'KeralaModelsBlogspot', 'reelsforyouu','actress_sexy',
    'hotactresstuff']


# Path to the JSON file that contains channel data
LAST_MESSAGE_FILE = 'last_message_ids.json'

# Load the last message IDs from the JSON file
def load_last_message_ids():
    if os.path.exists(LAST_MESSAGE_FILE):
        with open(LAST_MESSAGE_FILE, 'r') as file:
            return json.load(file)
    return {}

# Function to extract channel name from JSON key
def extract_channel_name(channel_key, channel_data):
    if channel_key.startswith('user_'):
        return channel_key.replace('user_', '')
    elif channel_key.startswith('id_'):
        return channel_data.get("Channel_Name", channel_key)  # Use 'Channel_Name' if available in the JSON
    return channel_key

# Find channels in the JSON file but not in DEFAULT_CHANNELS
def find_channels_in_json_not_in_default(json_channels, default_channels):
    # Channels present in the JSON but not in DEFAULT_CHANNELS
    return [channel for channel in json_channels if channel not in default_channels]

# Main function to find and print missing channels
def main():
    # Load the last message IDs from the file
    last_message_ids = load_last_message_ids()

    # Extract channel names from the JSON file
    json_channels = [
        {
            "channel_name": extract_channel_name(channel_key, channel_data),
            "channel_id": channel_data['id']
        }
        for channel_key, channel_data in last_message_ids.items()
    ]

    # Find the channels that are in the JSON but not in DEFAULT_CHANNELS
    channels_in_json_not_in_default = find_channels_in_json_not_in_default(
        [channel['channel_name'] for channel in json_channels],
        DEFAULT_CHANNELS
    )

    # Print the channel names and IDs that are present in the JSON but missing from DEFAULT_CHANNELS
    if channels_in_json_not_in_default:
        print("\nChannels in JSON but not in DEFAULT_CHANNELS:")
        for channel in json_channels:
            if channel['channel_name'] in channels_in_json_not_in_default:
                print(f"Channel Name: {channel['channel_name']}, Channel ID: {channel['channel_id']}")
    else:
        print("\nNo channels in JSON that are missing from DEFAULT_CHANNELS.")

if __name__ == '__main__':
    main()