import numpy as np
import pandas as pd

# Load data
df = pd.read_csv('Case_3_Media_Behavior.csv')
df.head()
df.columns.tolist()

def clean_data(df):
    df = df.copy()

    # Create dictionary for `column_mapping` and rename all of columns
    import json

    column_mapping = {
        # ข้อมูลประชากร (Demographics)
        'Timestamp': 'timestamp',
        'เพศ': 'gender',
        'อายุ': 'age',
        'อาชีพ': 'occupation',
        'ระดับการศึกษาสูงสุด': 'education_level',
        'รายได้ของคุณต่อเดือน': 'income_per_month',
        'โปรดพิมพ์จังหวัดที่อยู่อาศัยของคุณ เช่น กทม , ขอนแก่น, ชลบุรี': 'province',
        'คุณมีความสนใจในเรื่องใดบ้าง (เลือกได้หลายคำตอบ)': 'interests',

        # พฤติกรรมการเปิดรับสื่อโฆษณา (Media Exposure)
        'คุณเห็นสื่อโฆษณาผ่านช่องทางใดบ้าง (เลือกได้หลายคำตอบ)': 'ad_channels_seen',
        'คุณเห็นสื่อโฆษณาผ่านช่องทางใดบ่อยที่สุด': 'most_freq_ad_channel',
        'การรับชมโฆษณาผ่านช่องทางใดที่มีอิทธิพลต่อการตัดสินใจซื้อผลิตภัณฑ์ (เลือกได้หลายคำตอบ)': 'influential_ad_channels',
        'ในการรับชมโฆษณา คุณคิดว่าโฆษณาผ่านช่องทางใดมีความน่าเชื่อถือ (เลือกได้หลายคำตอบ)': 'trusted_ad_channels',
        'ในการรับชมโฆษณา คุณคิดว่าโฆษณาผ่านช่องทางใดมีความน่าเชื่อถือมากที่สุด': 'most_trusted_ad_channel',
        'คุณคิดว่าดารา/Presenter มีผลต่อการตัดสินใจซื้อสินค้าหรือไม่': 'presenter_influence',

        # ความถี่และระยะเวลาในการเสพสื่อ (Media Frequency & Duration)
        'ความถี่ในการเปิดรับสื่อในแต่ละช่องทางต่อสัปดาห์ [โทรทัศน์]': 'freq_tv_per_week',
        'ความถี่ในการเปิดรับสื่อในแต่ละช่องทางต่อสัปดาห์ [วิทยุ]': 'freq_radio_per_week',
        'ความถี่ในการเปิดรับสื่อในแต่ละช่องทางต่อสัปดาห์ [สื่อนอกบ้าน]': 'freq_ooh_per_week',
        'ความถี่ในการเปิดรับสื่อในแต่ละช่องทางต่อสัปดาห์ [ออนไลน์]': 'freq_online_per_week',
        'ระยะเวลาในการเสพสื่อต่อวัน ในแต่ละช่องทาง [โทรทัศน์]': 'duration_tv_per_day',
        'ระยะเวลาในการเสพสื่อต่อวัน ในแต่ละช่องทาง [วิทยุ]': 'duration_radio_per_day',
        'ระยะเวลาในการเสพสื่อต่อวัน ในแต่ละช่องทาง [สื่อนอกบ้าน]': 'duration_ooh_per_day',
        'ระยะเวลาในการเสพสื่อต่อวัน ในแต่ละช่องทาง [ออนไลน์]': 'duration_online_per_day',

        # ช่วงเวลาการเสพสื่อ (Time of Day)
        'ในวันจันทร์-ศุกร์ (Weekday) ช่วงเวลาใดที่คุณเปิดรับสื่อแต่ละช่องทาง [โทรทัศน์]': 'weekday_time_tv',
        'ในวันจันทร์-ศุกร์ (Weekday) ช่วงเวลาใดที่คุณเปิดรับสื่อแต่ละช่องทาง [วิทยุ]': 'weekday_time_radio',
        'ในวันจันทร์-ศุกร์ (Weekday) ช่วงเวลาใดที่คุณเปิดรับสื่อแต่ละช่องทาง [สื่อนอกบ้าน]': 'weekday_time_ooh',
        'ในวันจันทร์-ศุกร์ (Weekday) ช่วงเวลาใดที่คุณเปิดรับสื่อแต่ละช่องทาง [ออนไลน์]': 'weekday_time_online',
        'ในวันหยุดเสาร์-อาทิตย์ (Weekend) ช่วงเวลาใดที่คุณเปิดรับสื่อแต่ละช่องทาง [โทรทัศน์]': 'weekend_time_tv',
        'ในวันหยุดเสาร์-อาทิตย์ (Weekend) ช่วงเวลาใดที่คุณเปิดรับสื่อแต่ละช่องทาง [วิทยุ]': 'weekend_time_radio',
        'ในวันหยุดเสาร์-อาทิตย์ (Weekend) ช่วงเวลาใดที่คุณเปิดรับสื่อแต่ละช่องทาง [สื่อนอกบ้าน]': 'weekend_time_ooh',
        'ในวันหยุดเสาร์-อาทิตย์ (Weekend) ช่วงเวลาใดที่คุณเปิดรับสื่อแต่ละช่องทาง [ออนไลน์]': 'weekend_time_online',

        # รายละเอียดสื่อแต่ละประเภท (Media specifics)
        'คุณดูโทรทัศน์ช่องใดบ้าง (เลือกได้หลายคำตอบ)': 'tv_channels_watched',
        'คุณดูโทรทัศน์ช่องไหนบ่อยที่สุด 5 อันดับแรก (เลือกไม่เกิน 5 คำตอบ)': 'top5_tv_channels',
        'คุณดูรายการโทรทัศน์ประเภทใดบ้าง (เลือกได้หลายคำตอบ)': 'tv_program_types',
        'คุณดูรายการโทรทัศน์ผ่านช่องทางไหนบ้าง (เลือกได้หลายคำตอบ)': 'tv_platforms',
        'สื่อนอกบ้านประเภทไหนที่คุณเห็นโฆษณาเป็นประจำ (เลือกได้หลายคำตอบ)': 'ooh_types_seen',
        'สื่อนอกบ้านประเภทไหนที่คุณเห็นโฆษณาเป็นประจำมากที่สุด': 'most_freq_ooh_type',
        'สื่อวิทยุคลื่นอะไรคุณฟังเป็นประจำมากที่สุด': 'most_freq_radio_station',
        'คุณใช้โซเชียลมีเดียใดบ้าง (เลือกได้หลายคำตอบ)': 'social_media_used',
        'คุณใช้โซเชียลมีเดียใดบ่อยที่สุด': 'most_freq_social_media',
        'คุณดูวิดีโอ/ซีรีส์/หนัง จากแพลตฟอร์มใดบ้าง (เลือกได้หลายคำตอบ)': 'streaming_used',
        'คุณดูวิดีโอ/ซีรีส์/หนัง จากแพลตฟอร์มใดบ่อยที่สุด': 'most_freq_streaming',
        'คุณฟังเพลง/วิทยุ/รายการต่างๆ จากแพลตฟอร์มใดบ้าง (เลือกได้หลายคำตอบ)': 'audio_streaming_used',
        'คุณฟังเพลง/วิทยุ/รายการต่างๆ จากแพลตฟอร์มใดบ่อยที่สุด': 'most_freq_audio_streaming',

        # พฤติกรรมช่วงเทศกาล (Holiday Behavior)
        'ในวันหยุดยาวหรือเทศกาล เช่น ช่วงสงกรานต์ คุณดูโทรทัศน์ อย่างไร': 'holiday_tv_behavior',
        'ในวันหยุดยาวหรือเทศกาล คุณใช้โซเชียลมีเดีย อย่างไร': 'holiday_social_behavior',
        'ในวันหยุดยาวหรือเทศกาล คุณดูวิดีโอ/หนัง/ซีรีส์ อย่างไร': 'holiday_streaming_behavior',
        'ในวันหยุดยาวหรือเทศกาล คุณฟังเพลง/วิทยุ อย่างไร': 'holiday_audio_behavior',

        # พฤติกรรมการดื่มกาแฟ (Coffee Consumption)
        'คุณดื่มกาแฟหรือไม่': 'drink_coffee',
        'คุณดื่มกาแฟประเภทใดบ้าง': 'coffee_types',
        'คุณดื่มกาแฟประเภทใดบ่อยที่สุด': 'most_freq_coffee_type',
        'คุณดื่มกาแฟประเภทใดบ้างคุณดื่มกาแฟประเภทใดบ่อยที่สุด': 'most_freq_coffee_type_merged',
        'คุณชอบกาแฟประเภทใดมากที่สุด': 'fav_coffee_type',
        'คุณดื่มกาแฟพร้อมดื่ม (Ready to drink) แบรนด์ใดบ้าง (เลือกได้หลายคำตอบ)': 'rtd_coffee_brands',
        'คุณดื่มกาแฟพร้อมดื่ม (Ready to drink) แบรนด์ใดบ่อยที่สุด': 'most_freq_rtd_coffee_brand',
        'คุณดื่มกาแฟพร้อมดื่ม (Ready to drink) ในโอกาส/โมเมนต์ใดบ้าง (เลือกได้หลายคำตอบ)': 'rtd_coffee_occasions',

        # ปัจจัยการเลือกซื้อกาแฟ RTD (RTD Coffee Factors)
        'ในการดื่มกาแฟพร้อมดื่ม (Ready to drink) คุณให้ความสำคัญกับคุณสมบัติด้านล่างนี้มากน้อยเพียงใด (5 = สำคัญมากที่สุด) [รสชาติดีเหมือนกาแฟสด]': 'coffee_factor_fresh_taste',
        'ในการดื่มกาแฟพร้อมดื่ม (Ready to drink) คุณให้ความสำคัญกับคุณสมบัติด้านล่างนี้มากน้อยเพียงใด (5 = สำคัญมากที่สุด) [รสชาติเข้มข้น]': 'coffee_factor_intensity',
        'ในการดื่มกาแฟพร้อมดื่ม (Ready to drink) คุณให้ความสำคัญกับคุณสมบัติด้านล่างนี้มากน้อยเพียงใด (5 = สำคัญมากที่สุด) [รสชาตินุ่มละมุน]': 'coffee_factor_smoothness',
        'ในการดื่มกาแฟพร้อมดื่ม (Ready to drink) คุณให้ความสำคัญกับคุณสมบัติด้านล่างนี้มากน้อยเพียงใด (5 = สำคัญมากที่สุด) [รสชาติเปรี้ยว]': 'coffee_factor_acidity',
        'ในการดื่มกาแฟพร้อมดื่ม (Ready to drink) คุณให้ความสำคัญกับคุณสมบัติด้านล่างนี้มากน้อยเพียงใด (5 = สำคัญมากที่สุด) [กลิ่นหอมกาแฟ]': 'coffee_factor_aroma',
        'ในการดื่มกาแฟพร้อมดื่ม (Ready to drink) คุณให้ความสำคัญกับคุณสมบัติด้านล่างนี้มากน้อยเพียงใด (5 = สำคัญมากที่สุด) [ต้องการความดีด/ตื่นตัวจากคาเฟอีน]': 'coffee_factor_caffeine',
        'ในการดื่มกาแฟพร้อมดื่ม (Ready to drink) คุณให้ความสำคัญกับคุณสมบัติด้านล่างนี้มากน้อยเพียงใด (5 = สำคัญมากที่สุด) [แหล่งที่มาของเมล็ดกาแฟ เช่น เมล็ดนำเข้า]': 'coffee_factor_origin',
        'ในการดื่มกาแฟพร้อมดื่ม (Ready to drink) คุณให้ความสำคัญกับคุณสมบัติด้านล่างนี้มากน้อยเพียงใด (5 = สำคัญมากที่สุด) [ความสะดวก/พกพาง่าย/ไม่เลอะเทอะ]': 'coffee_factor_convenience',
        'ในการดื่มกาแฟพร้อมดื่ม (Ready to drink) คุณให้ความสำคัญกับคุณสมบัติด้านล่างนี้มากน้อยเพียงใด (5 = สำคัญมากที่สุด) [ประหยัดกว่ากินกาแฟสดตามร้าน]': 'coffee_factor_economy',
        'ในการดื่มกาแฟพร้อมดื่ม (Ready to drink) คุณให้ความสำคัญกับคุณสมบัติด้านล่างนี้มากน้อยเพียงใด (5 = สำคัญมากที่สุด) [มีฉลากเห็นข้อมูลโภชนาการ (Nutrition facts)]': 'coffee_factor_nutrition',
        'ในการดื่มกาแฟพร้อมดื่ม (Ready to drink) คุณให้ความสำคัญกับคุณสมบัติด้านล่างนี้มากน้อยเพียงใด (5 = สำคัญมากที่สุด) [แบรนด์ดัง น่าเชื่อถือ]': 'coffee_factor_brand_trust',
        'ในการดื่มกาแฟพร้อมดื่ม (Ready to drink) คุณให้ความสำคัญกับคุณสมบัติด้านล่างนี้มากน้อยเพียงใด (5 = สำคัญมากที่สุด) [ภาพลักษณ์ดูดี ดูพรีเมียม]': 'coffee_factor_premium_image',
        'ในการดื่มกาแฟพร้อมดื่ม (Ready to drink) คุณให้ความสำคัญกับคุณสมบัติด้านล่างนี้มากน้อยเพียงใด (5 = สำคัญมากที่สุด) [แพ็คเกจ/ขวดสวย]': 'coffee_factor_packaging',

        # ความคิดเห็นต่อแบรนด์ (Brand Perception)
        'คุณชอบดื่มกาแฟร้าน Cafe Amazon หรือไม่': 'like_cafe_amazon',
        'สำหรับคนที่ชอบดื่มกาแฟ Cafe Amazon รบกวนเขียนเหตุผลที่ชอบดื่มสั้นๆ': 'reason_like_amazon',
        'สำหรับคนที่ไม่ชอบดื่มกาแฟ Cafe Amazon รบกวนเขียนเหตุผลที่ไม่ชอบดื่มสั้นๆ': 'reason_dislike_amazon',
        'คุณรู้จักกาแฟแบรนด์ใหม่จากที่สื่อบ้าง (เลือกได้หลายคำตอบ)': 'new_coffee_discovery_media',
        'ถ้ามีแบรนด์กาแฟพร้อมดื่ม (Ready to drink) ออกใหม่ คุณจะลองหรือไม่': 'will_try_new_rtd_coffee',

        # อิทธิพลต่อการซื้อกาแฟ (Coffee Influencers)
        'บุคคลต่อไปนี้มีอิทธิพลในการซื้อกาแฟพร้อมดื่ม (Ready to drink) ของคุณ มากน้อยเพียงใด โปรดเรียงตามลำดับ โดยไม่ซ้ำกัน [รีวิวจากดารา]': 'coffee_influence_celebrity',
        'บุคคลต่อไปนี้มีอิทธิพลในการซื้อกาแฟพร้อมดื่ม (Ready to drink) ของคุณ มากน้อยเพียงใด โปรดเรียงตามลำดับ โดยไม่ซ้ำกัน [รีวิวจากบล็อกเกอร์สายอาหารและเครื่องดื่ม เช่น กินหนม, ถนัดชิม]': 'coffee_influence_food_blogger',
        'บุคคลต่อไปนี้มีอิทธิพลในการซื้อกาแฟพร้อมดื่ม (Ready to drink) ของคุณ มากน้อยเพียงใด โปรดเรียงตามลำดับ โดยไม่ซ้ำกัน [รีวิวจากบล็อกเกอร์สายกาแฟ เช่น บาริสต้า, Cafe hopper]': 'coffee_influence_coffee_blogger',
        'บุคคลต่อไปนี้มีอิทธิพลในการซื้อกาแฟพร้อมดื่ม (Ready to drink) ของคุณ มากน้อยเพียงใด โปรดเรียงตามลำดับ โดยไม่ซ้ำกัน [รีวิวจากบล็อกเกอร์สายไลฟ์สไตล์/บันเทิง เช่น เทพลีลา]': 'coffee_influence_lifestyle_blogger',
        'บุคคลต่อไปนี้มีอิทธิพลในการซื้อกาแฟพร้อมดื่ม (Ready to drink) ของคุณ มากน้อยเพียงใด โปรดเรียงตามลำดับ โดยไม่ซ้ำกัน [เพื่อน ครอบครัว และคนใกล้ตัว]': 'coffee_influence_friends_family',
        'คุณซื้อกาแฟพร้อมดื่ม (Ready to drink) จากช่องทางใดบ้าง': 'rtd_coffee_purchase_channels',

        # พฤติกรรมการดื่มชา (Tea Consumption)
        'คุณดื่มชาหรือไม่': 'drink_tea',
        'คุณดื่มชาแบบใดบ้าง (เลือกได้หลายคำตอบ)': 'tea_types',
        'คุณดื่มชาประเภทใดบ่อยที่สุด': 'most_freq_tea_type',
        'คุณชอบดื่มชาประเภทใดมากที่สุด': 'fav_tea_type',
        'จากตัวเลือกด้านบน รบกวนบอกเหตุผลสั้นๆ ทำไมคุณถึงชอบดื่มชาประเภทนั้นๆ (ชาแก้ว/ชาพร้อมดื่ม/ชงเอง)': 'reason_fav_tea',
        'คุณดื่มชาพร้อมดื่ม แบรนด์ใดบ้าง (เลือกได้หลายคำตอบ)': 'rtd_tea_brands',
        'คุณดื่มชาพร้อมดื่ม (Ready to drink) แบรนด์ใดบ่อยที่สุด': 'most_freq_rtd_tea_brand',
        'คุณดื่มชาพร้อมดื่ม ในโอกาส/โมเมนต์ใดบ้าง (เลือกได้หลายคำตอบ)': 'rtd_tea_occasions',

        # ปัจจัยการเลือกซื้อชา RTD (RTD Tea Factors)
        'ในการดื่มชาพร้อมดื่ม (Ready to drink) คุณให้ความสำคัญกับคุณสมบัติด้านล่างนี้มากน้อยเพียงใด (5 = สำคัญมากที่สุด) [กลิ่นหอมใบชาเขียว]': 'tea_factor_aroma',
        'ในการดื่มชาพร้อมดื่ม (Ready to drink) คุณให้ความสำคัญกับคุณสมบัติด้านล่างนี้มากน้อยเพียงใด (5 = สำคัญมากที่สุด) [รสชาติชาเขียวเข้มข้น]': 'tea_factor_intensity',
        'ในการดื่มชาพร้อมดื่ม (Ready to drink) คุณให้ความสำคัญกับคุณสมบัติด้านล่างนี้มากน้อยเพียงใด (5 = สำคัญมากที่สุด) [ไม่เติมน้ำตาล/ไม่มีน้ำตาล]': 'tea_factor_no_sugar',
        'ในการดื่มชาพร้อมดื่ม (Ready to drink) คุณให้ความสำคัญกับคุณสมบัติด้านล่างนี้มากน้อยเพียงใด (5 = สำคัญมากที่สุด) [ไม่มีแคลอรี่ (0 kcal)]': 'tea_factor_zero_kcal',
        'ในการดื่มชาพร้อมดื่ม (Ready to drink) คุณให้ความสำคัญกับคุณสมบัติด้านล่างนี้มากน้อยเพียงใด (5 = สำคัญมากที่สุด) [มีฉลากเห็นข้อมูลโภชนาการ (Nutrition facts)]': 'tea_factor_nutrition',
        'ในการดื่มชาพร้อมดื่ม (Ready to drink) คุณให้ความสำคัญกับคุณสมบัติด้านล่างนี้มากน้อยเพียงใด (5 = สำคัญมากที่สุด) [แหล่งที่มาของใบชา เช่น ญี่ปุ่น]': 'tea_factor_origin',
        'ในการดื่มชาพร้อมดื่ม (Ready to drink) คุณให้ความสำคัญกับคุณสมบัติด้านล่างนี้มากน้อยเพียงใด (5 = สำคัญมากที่สุด) [วิธีการชง/สกัดชาเขียว เช่น สกัดเย็น]': 'tea_factor_brewing_method',
        'ในการดื่มชาพร้อมดื่ม (Ready to drink) คุณให้ความสำคัญกับคุณสมบัติด้านล่างนี้มากน้อยเพียงใด (5 = สำคัญมากที่สุด) [ความสะดวก/พกพาง่าย/ไม่เลอะเทอะ]': 'tea_factor_convenience',
        'ในการดื่มชาพร้อมดื่ม (Ready to drink) คุณให้ความสำคัญกับคุณสมบัติด้านล่างนี้มากน้อยเพียงใด (5 = สำคัญมากที่สุด) [แบรนด์ดัง น่าเชื่อถือ]': 'tea_factor_brand_trust',
        'ในการดื่มชาพร้อมดื่ม (Ready to drink) คุณให้ความสำคัญกับคุณสมบัติด้านล่างนี้มากน้อยเพียงใด (5 = สำคัญมากที่สุด) [ภาพลักษณ์ดูดี ดูพรีเมียม]': 'tea_factor_premium_image',
        'ในการดื่มชาพร้อมดื่ม (Ready to drink) คุณให้ความสำคัญกับคุณสมบัติด้านล่างนี้มากน้อยเพียงใด (5 = สำคัญมากที่สุด) [แพ็คเกจ/ขวดสวย]': 'tea_factor_packaging',

        # อิทธิพลต่อการซื้อชา (Tea Influencers)
        'คุณรู้จักชาแบรนด์ใหม่จากที่สื่อบ้าง(เลือกได้หลายคำตอบ)': 'new_tea_discovery_media',
        'ถ้ามีแบรนด์ชาพร้อมดื่ม (Ready to drink) ออกใหม่ คุณจะลองหรือไม่': 'will_try_new_rtd_tea',
        'บุคคลต่อไปนี้มีอิทธิพลในการซื้อชาพร้อมดื่ม (Ready to drink) ของคุณ มากน้อยเพียงใด โปรดเรียงตามลำดับ โดยไม่ซ้ำกัน [รีวิวจากดารา]': 'tea_influence_celebrity',
        'บุคคลต่อไปนี้มีอิทธิพลในการซื้อชาพร้อมดื่ม (Ready to drink) ของคุณ มากน้อยเพียงใด โปรดเรียงตามลำดับ โดยไม่ซ้ำกัน [รีวิวจากบล็อกเกอร์สายอาหารและเครื่องดื่ม เช่น กินหนม, ถนัดชิม]': 'tea_influence_food_blogger',
        'บุคคลต่อไปนี้มีอิทธิพลในการซื้อชาพร้อมดื่ม (Ready to drink) ของคุณ มากน้อยเพียงใด โปรดเรียงตามลำดับ โดยไม่ซ้ำกัน [รีวิวจากบล็อกเกอร์สายสุขภาพ/สายคลีน]': 'tea_influence_health_blogger',
        'บุคคลต่อไปนี้มีอิทธิพลในการซื้อชาพร้อมดื่ม (Ready to drink) ของคุณ มากน้อยเพียงใด โปรดเรียงตามลำดับ โดยไม่ซ้ำกัน [รีวิวจากบล็อกเกอร์สายไลฟ์สไตล์/บันเทิง เช่น เทพลีลา]': 'tea_influence_lifestyle_blogger',
        'บุคคลต่อไปนี้มีอิทธิพลในการซื้อชาพร้อมดื่ม (Ready to drink) ของคุณ มากน้อยเพียงใด โปรดเรียงตามลำดับ โดยไม่ซ้ำกัน [เพื่อน ครอบครัว และคนใกล้ตัว]': 'tea_influence_friends_family',
        'คุณซื้อชาพร้อมดื่ม (Ready to drink) จากช่องทางใดบ้าง': 'rtd_tea_purchase_channels'
    }
    df.rename(columns=column_mapping, inplace=True)

    # Save to JSON (Data Dictionary)
    with open('column_mapping.json', 'w', encoding='utf-8') as f:
        json.dump(column_mapping, f, ensure_ascii=False, indent=4)
    print("Dictionary has been saved as a 'column_mapping.json' file.")

    # Manage Datetime features
    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
    df['hour'] = df['timestamp'].dt.hour
    df['day_of_week'] = df['timestamp'].dt.day_name()
    df['month'] = df['timestamp'].dt.month_name()
    print(df[['timestamp']].head())

    # Clean and distribute the list of provinces (Explode)
    if 'province' in df.columns:
        df['province'] = df['province'].fillna('').astype(str)
        df['province'] = df['province'].str.split(',')

        df = df.explode('province')
        df['province'] = df['province'].str.strip()
        
        df['province'] = df['province'].replace(
            ['กทม', 'กทม.', 'กรุงเทพ', 'dกทม', 'กมม', 'bangkok', 'bkk', 'Bkk'],
            'กรุงเทพมหานคร',
        )
        df['province'] = df['province'].replace(
            ['พัทยา', 'แอลเอ', 'Bonn'],
            ['ชลบุรี', 'ต่างประเทศ', 'ต่างประเทศ']
        )

    # Manage multiple answer columns
    multi_answer_cols = [
        'interests', 'ad_channels_seen', 'influential_ad_channels',
        'trusted_ad_channels', 'tv_channels_watched', 'top5_tv_channels',
        'tv_program_types', 'tv_platforms', 'ooh_types_seen',
        'social_media_used', 'streaming_used', 'audio_streaming_used',
        'coffee_types', 'rtd_coffee_brands', 'rtd_coffee_occasions',
        'new_coffee_discovery_media', 'will_try_new_rtd_coffee',
        'rtd_coffee_purchase_channels', 'tea_types', 'rtd_tea_brands',
        'rtd_tea_occasions', 'new_tea_discovery_media',
        'will_try_new_rtd_tea', 'rtd_tea_purchase_channels'
    ]
    for col in multi_answer_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.replace(', ', ',', regex=False)

    # Manage Null for people who "ไม่ดื่ม" coffee/tea
    coffee_choice_cols = [
        'coffee_types', 'most_freq_coffee_type', 'most_freq_coffee_type_merged',
        'fav_coffee_type', 'rtd_coffee_brands', 'most_freq_rtd_coffee_brand',
        'rtd_coffee_occasions'
    ]
    for col in coffee_choice_cols:
        if col in df.columns and 'drink_coffee' in df.columns:
            df.loc[df['drink_coffee'] == 'ไม่ดื่ม', col] = None

    tea_choice_cols = [
        'tea_types', 'most_freq_tea_type', 'fav_tea_type', 'reason_fav_tea',
        'rtd_tea_brands', 'most_freq_rtd_tea_brand', 'rtd_tea_occasions'
    ]
    for col in tea_choice_cols:
        if col in df.columns and 'drink_tea' in df.columns:
            df.loc[df['drink_tea'] == 'ไม่ดื่ม', col] = None

    # Add 'ไม่ระบุ' for those who drink but don't answer
    for col in coffee_choice_cols:
        if col in df.columns:
            df[col] = df[col].fillna('ไม่ระบุ')

    for col in tea_choice_cols:
        if col in df.columns:
            df[col] = df[col].fillna('ไม่ระบุ')

    # Convert Rating, the importance of coffee/tea factors
    rating_mapping = {
        '5 สำคัญมากที่สุด': 5.0,
        '4 สำคัญ': 4.0,
        '3 เฉยๆ': 3.0,
        '2 ไม่สำคัญ': 2.0,
        '1 ไม่สำคัญเลย': 1.0,
        'ไม่ระบุ': None,
    }
    factor_cols = [
        'coffee_factor_fresh_taste', 'coffee_factor_intensity',
        'coffee_factor_smoothness', 'coffee_factor_acidity',
        'coffee_factor_aroma', 'coffee_factor_caffeine',
        'coffee_factor_origin', 'coffee_factor_convenience',
        'coffee_factor_economy', 'coffee_factor_nutrition',
        'coffee_factor_brand_trust', 'coffee_factor_premium_image',
        'coffee_factor_packaging',
        'tea_factor_aroma', 'tea_factor_intensity',
        'tea_factor_no_sugar', 'tea_factor_zero_kcal',
        'tea_factor_nutrition', 'tea_factor_origin',
        'tea_factor_brewing_method', 'tea_factor_convenience',
        'tea_factor_brand_trust', 'tea_factor_premium_image',
        'tea_factor_packaging'
    ]
    for col in factor_cols:
        if col in df.columns:
            df[col] = df[col].replace(rating_mapping)

    # Convert Media Influence Rating (Coffee)
    rating_mapping_coffee_inf = {
        '5 มีอิทธิพลมากที่สุด': 5.0,
        '4 มีอิทธิพล': 4.0,
        '3 ปานกลาง': 3.0,
        '2 ไม่มีอิทธิพล': 2.0,
        '1 ไม่มีอิทธิพลเลย': 1.0,
        'ไม่ระบุ': None
    }
    coffee_influencer_cols = [
        'coffee_influence_celebrity', 'coffee_influence_food_blogger',
        'coffee_influence_coffee_blogger', 'coffee_influence_lifestyle_blogger',
        'coffee_influence_friends_family'
    ]
    for col in coffee_influencer_cols:
        if col in df.columns:
            df[col] = df[col].replace(rating_mapping_coffee_inf)

    # Convert Media Influence Rating (Tea)
    rating_mapping_tea_inf = {
        '5 มีอิทธิพลมาก': 5.0,
        '4 มีอิทธิพล': 4.0,
        '3 ปานกลาง': 3.0,
        '2 ไม่มีอิทธิพล': 2.0,
        '1 ไม่มีอิทธิพลเลย': 1.0,
        'ไม่ระบุ': None
    }
    tea_influencer_cols = [
        'tea_influence_celebrity', 'tea_influence_food_blogger',
        'tea_influence_health_blogger', 'tea_influence_lifestyle_blogger',
        'tea_influence_friends_family'
    ]
    for col in tea_influencer_cols:
        if col in df.columns:
            df[col] = df[col].replace(rating_mapping_tea_inf)

    return df
