import numpy as np
import pandas as pd
import json

def clean_data(df):
    df = df.copy()

    # Handle Incomplete Responses
    if 'เพศ' in df.columns and 'อายุ' in df.columns:
        df = df.dropna(subset=['เพศ', 'อายุ'])

    col_map = {
        # ข้อมูลประชากร (Demographics)
        'Timestamp': 'timestamp',
        'เพศ': 'gender',
        'อายุ': 'age',
        'อาชีพ': 'occupation',
        'ระดับการศึกษาสูงสุด': 'education',
        'รายได้ของคุณต่อเดือน': 'income',
        'โปรดพิมพ์จังหวัดที่อยู่อาศัยของคุณ เช่น กทม , ขอนแก่น, ชลบุรี': 'province',
        'คุณมีความสนใจในเรื่องใดบ้าง (เลือกได้หลายคำตอบ)': 'interests',

        # พฤติกรรมการเปิดรับสื่อโฆษณา (Media Exposure)
        'คุณเห็นสื่อโฆษณาผ่านช่องทางใดบ้าง (เลือกได้หลายคำตอบ)': 'ad_channels_seen',
        'คุณเห็นสื่อโฆษณาผ่านช่องทางใดบ่อยที่สุด': 'most_ad_channels',
        'การรับชมโฆษณาผ่านช่องทางใดที่มีอิทธิพลต่อการตัดสินใจซื้อผลิตภัณฑ์ (เลือกได้หลายคำตอบ)': 'influence_ad',
        'ในการรับชมโฆษณา คุณคิดว่าโฆษณาผ่านช่องทางใดมีความน่าเชื่อถือ (เลือกได้หลายคำตอบ)': 'trusted_ad',
        'ในการรับชมโฆษณา คุณคิดว่าโฆษณาผ่านช่องทางใดมีความน่าเชื่อถือมากที่สุด': 'most_trusted_ad',
        'คุณคิดว่าดารา/Presenter มีผลต่อการตัดสินใจซื้อสินค้าหรือไม่': 'presenter_effect',

        # ความถี่และระยะเวลาในการเสพสื่อ (Media Frequency & Duration)
        'ความถี่ในการเปิดรับสื่อในแต่ละช่องทางต่อสัปดาห์ [โทรทัศน์]': 'freq_tv',
        'ความถี่ในการเปิดรับสื่อในแต่ละช่องทางต่อสัปดาห์ [วิทยุ]': 'freq_radio',
        'ความถี่ในการเปิดรับสื่อในแต่ละช่องทางต่อสัปดาห์ [สื่อนอกบ้าน]': 'freq_ooh',
        'ความถี่ในการเปิดรับสื่อในแต่ละช่องทางต่อสัปดาห์ [ออนไลน์]': 'freq_online',
        'ระยะเวลาในการเสพสื่อต่อวัน ในแต่ละช่องทาง [โทรทัศน์]': 'dur_tv',
        'ระยะเวลาในการเสพสื่อต่อวัน ในแต่ละช่องทาง [วิทยุ]': 'dur_radio',
        'ระยะเวลาในการเสพสื่อต่อวัน ในแต่ละช่องทาง [สื่อนอกบ้าน]': 'dur_ooh',
        'ระยะเวลาในการเสพสื่อต่อวัน ในแต่ละช่องทาง [ออนไลน์]': 'dur_online',

        # ช่วงเวลาการเสพสื่อ (Time of Day)
        'ในวันจันทร์-ศุกร์ (Weekday) ช่วงเวลาใดที่คุณเปิดรับสื่อแต่ละช่องทาง [โทรทัศน์]': 'weekday_tv',
        'ในวันจันทร์-ศุกร์ (Weekday) ช่วงเวลาใดที่คุณเปิดรับสื่อแต่ละช่องทาง [วิทยุ]': 'weekday_radio',
        'ในวันจันทร์-ศุกร์ (Weekday) ช่วงเวลาใดที่คุณเปิดรับสื่อแต่ละช่องทาง [สื่อนอกบ้าน]': 'weekday_ooh',
        'ในวันจันทร์-ศุกร์ (Weekday) ช่วงเวลาใดที่คุณเปิดรับสื่อแต่ละช่องทาง [ออนไลน์]': 'weekday_online',
        'ในวันหยุดเสาร์-อาทิตย์ (Weekend) ช่วงเวลาใดที่คุณเปิดรับสื่อแต่ละช่องทาง [โทรทัศน์]': 'weekend_tv',
        'ในวันหยุดเสาร์-อาทิตย์ (Weekend) ช่วงเวลาใดที่คุณเปิดรับสื่อแต่ละช่องทาง [วิทยุ]': 'weekend_radio',
        'ในวันหยุดเสาร์-อาทิตย์ (Weekend) ช่วงเวลาใดที่คุณเปิดรับสื่อแต่ละช่องทาง [สื่อนอกบ้าน]': 'weekend_ooh',
        'ในวันหยุดเสาร์-อาทิตย์ (Weekend) ช่วงเวลาใดที่คุณเปิดรับสื่อแต่ละช่องทาง [ออนไลน์]': 'weekend_online',

        # รายละเอียดสื่อแต่ละประเภท (Media specifics)
        'คุณดูโทรทัศน์ช่องใดบ้าง (เลือกได้หลายคำตอบ)': 'tv_channels',
        'คุณดูโทรทัศน์ช่องไหนบ่อยที่สุด 5 อันดับแรก (เลือกไม่เกิน 5 คำตอบ)': 'top5_channels',
        'คุณดูรายการโทรทัศน์ประเภทใดบ้าง (เลือกได้หลายคำตอบ)': 'tv_program_types',
        'คุณดูรายการโทรทัศน์ผ่านช่องทางไหนบ้าง (เลือกได้หลายคำตอบ)': 'tv_platforms',
        'สื่อนอกบ้านประเภทไหนที่คุณเห็นโฆษณาเป็นประจำ (เลือกได้หลายคำตอบ)': 'ooh_types_seen',
        'สื่อนอกบ้านประเภทไหนที่คุณเห็นโฆษณาเป็นประจำมากที่สุด': 'most_freq_ooh',
        'สื่อวิทยุคลื่นอะไรคุณฟังเป็นประจำมากที่สุด': 'most_freq_radio',
        'คุณใช้โซเชียลมีเดียใดบ้าง (เลือกได้หลายคำตอบ)': 'social_media_used',
        'คุณใช้โซเชียลมีเดียใดบ่อยที่สุด': 'most_freq_social_media',
        'คุณดูวิดีโอ/ซีรีส์/หนัง จากแพลตฟอร์มใดบ้าง (เลือกได้หลายคำตอบ)': 'streaming_used',
        'คุณดูวิดีโอ/ซีรีส์/หนัง จากแพลตฟอร์มใดบ่อยที่สุด': 'most_freq_streaming',
        'คุณฟังเพลง/วิทยุ/รายการต่างๆ จากแพลตฟอร์มใดบ้าง (เลือกได้หลายคำตอบ)': 'audio_streaming_used',
        'คุณฟังเพลง/วิทยุ/รายการต่างๆ จากแพลตฟอร์มใดบ่อยที่สุด': 'most_freq_audio_streaming',

        # พฤติกรรมช่วงเทศกาล (Holiday Behavior)
        'ในวันหยุดยาวหรือเทศกาล เช่น ช่วงสงกรานต์ คุณดูโทรทัศน์ อย่างไร': 'holiday_tv',
        'ในวันหยุดยาวหรือเทศกาล คุณใช้โซเชียลมีเดีย อย่างไร': 'holiday_social',
        'ในวันหยุดยาวหรือเทศกาล คุณดูวิดีโอ/หนัง/ซีรีส์ อย่างไร': 'holiday_streaming',
        'ในวันหยุดยาวหรือเทศกาล คุณฟังเพลง/วิทยุ อย่างไร': 'holiday_audio',

        # พฤติกรรมการดื่มกาแฟ (Coffee Consumption)
        'คุณดื่มกาแฟหรือไม่': 'drink_coffee',
        'คุณดื่มกาแฟประเภทใดบ้าง': 'coffee_types',
        'คุณดื่มกาแฟประเภทใดบ่อยที่สุด': 'most_freq_coffee',
        'คุณดื่มกาแฟประเภทใดบ้างคุณดื่มกาแฟประเภทใดบ่อยที่สุด': 'most_freq_coffee_merged',
        'คุณชอบกาแฟประเภทใดมากที่สุด': 'fav_coffee_type',
        'คุณดื่มกาแฟพร้อมดื่ม (Ready to drink) แบรนด์ใดบ้าง (เลือกได้หลายคำตอบ)': 'rtd_coffee_brands',
        'คุณดื่มกาแฟพร้อมดื่ม (Ready to drink) แบรนด์ใดบ่อยที่สุด': 'most_freq_rtd_brand',
        'คุณดื่มกาแฟพร้อมดื่ม (Ready to drink) ในโอกาส/โมเมนต์ใดบ้าง (เลือกได้หลายคำตอบ)': 'rtd_coffee_occasions',

        # ปัจจัยการเลือกซื้อกาแฟ RTD (RTD Coffee Factors)
        'ในการดื่มกาแฟพร้อมดื่ม (Ready to drink) คุณให้ความสำคัญกับคุณสมบัติด้านล่างนี้มากน้อยเพียงใด (5 = สำคัญมากที่สุด) [รสชาติดีเหมือนกาแฟสด]': 'coffee_fresh_taste',
        'ในการดื่มกาแฟพร้อมดื่ม (Ready to drink) คุณให้ความสำคัญกับคุณสมบัติด้านล่างนี้มากน้อยเพียงใด (5 = สำคัญมากที่สุด) [รสชาติเข้มข้น]': 'coffee_intensity',
        'ในการดื่มกาแฟพร้อมดื่ม (Ready to drink) คุณให้ความสำคัญกับคุณสมบัติด้านล่างนี้มากน้อยเพียงใด (5 = สำคัญมากที่สุด) [รสชาตินุ่มละมุน]': 'coffee_smooth',
        'ในการดื่มกาแฟพร้อมดื่ม (Ready to drink) คุณให้ความสำคัญกับคุณสมบัติด้านล่างนี้มากน้อยเพียงใด (5 = สำคัญมากที่สุด) [รสชาติเปรี้ยว]': 'coffee_acidity',
        'ในการดื่มกาแฟพร้อมดื่ม (Ready to drink) คุณให้ความสำคัญกับคุณสมบัติด้านล่างนี้มากน้อยเพียงใด (5 = สำคัญมากที่สุด) [กลิ่นหอมกาแฟ]': 'coffee_aroma',
        'ในการดื่มกาแฟพร้อมดื่ม (Ready to drink) คุณให้ความสำคัญกับคุณสมบัติด้านล่างนี้มากน้อยเพียงใด (5 = สำคัญมากที่สุด) [ต้องการความดีด/ตื่นตัวจากคาเฟอีน]': 'coffee_caffeine',
        'ในการดื่มกาแฟพร้อมดื่ม (Ready to drink) คุณให้ความสำคัญกับคุณสมบัติด้านล่างนี้มากน้อยเพียงใด (5 = สำคัญมากที่สุด) [แหล่งที่มาของเมล็ดกาแฟ เช่น เมล็ดนำเข้า]': 'coffee_origin',
        'ในการดื่มกาแฟพร้อมดื่ม (Ready to drink) คุณให้ความสำคัญกับคุณสมบัติด้านล่างนี้มากน้อยเพียงใด (5 = สำคัญมากที่สุด) [ความสะดวก/พกพาง่าย/ไม่เลอะเทอะ]': 'coffee_convenience',
        'ในการดื่มกาแฟพร้อมดื่ม (Ready to drink) คุณให้ความสำคัญกับคุณสมบัติด้านล่างนี้มากน้อยเพียงใด (5 = สำคัญมากที่สุด) [ประหยัดกว่ากินกาแฟสดตามร้าน]': 'coffee_value',
        'ในการดื่มกาแฟพร้อมดื่ม (Ready to drink) คุณให้ความสำคัญกับคุณสมบัติด้านล่างนี้มากน้อยเพียงใด (5 = สำคัญมากที่สุด) [มีฉลากเห็นข้อมูลโภชนาการ (Nutrition facts)]': 'coffee_nutrition',
        'ในการดื่มกาแฟพร้อมดื่ม (Ready to drink) คุณให้ความสำคัญกับคุณสมบัติด้านล่างนี้มากน้อยเพียงใด (5 = สำคัญมากที่สุด) [แบรนด์ดัง น่าเชื่อถือ]': 'coffee_brand_trust',
        'ในการดื่มกาแฟพร้อมดื่ม (Ready to drink) คุณให้ความสำคัญกับคุณสมบัติด้านล่างนี้มากน้อยเพียงใด (5 = สำคัญมากที่สุด) [ภาพลักษณ์ดูดี ดูพรีเมียม]': 'coffee_premium',
        'ในการดื่มกาแฟพร้อมดื่ม (Ready to drink) คุณให้ความสำคัญกับคุณสมบัติด้านล่างนี้มากน้อยเพียงใด (5 = สำคัญมากที่สุด) [แพ็คเกจ/ขวดสวย]': 'coffee_packaging',

        # ความคิดเห็นต่อแบรนด์ (Brand Perception)
        'คุณชอบดื่มกาแฟร้าน Cafe Amazon หรือไม่': 'like_cafe_amazon',
        'สำหรับคนที่ชอบดื่มกาแฟ Cafe Amazon รบกวนเขียนเหตุผลที่ชอบดื่มสั้นๆ': 'reason_like',
        'สำหรับคนที่ไม่ชอบดื่มกาแฟ Cafe Amazon รบกวนเขียนเหตุผลที่ไม่ชอบดื่มสั้นๆ': 'reason_dislike',
        'คุณรู้จักกาแฟแบรนด์ใหม่จากที่สื่อบ้าง (เลือกได้หลายคำตอบ)': 'new_coffee_discovery',
        'ถ้ามีแบรนด์กาแฟพร้อมดื่ม (Ready to drink) ออกใหม่ คุณจะลองหรือไม่': 'will_try_new_rtd_coffee',

        # อิทธิพลต่อการซื้อกาแฟ (Coffee Influencers)
        'บุคคลต่อไปนี้มีอิทธิพลในการซื้อกาแฟพร้อมดื่ม (Ready to drink) ของคุณ มากน้อยเพียงใด โปรดเรียงตามลำดับ โดยไม่ซ้ำกัน [รีวิวจากดารา]': 'coffee_celebrity',
        'บุคคลต่อไปนี้มีอิทธิพลในการซื้อกาแฟพร้อมดื่ม (Ready to drink) ของคุณ มากน้อยเพียงใด โปรดเรียงตามลำดับ โดยไม่ซ้ำกัน [รีวิวจากบล็อกเกอร์สายอาหารและเครื่องดื่ม เช่น กินหนม, ถนัดชิม]': 'coffee_food_blogger',
        'บุคคลต่อไปนี้มีอิทธิพลในการซื้อกาแฟพร้อมดื่ม (Ready to drink) ของคุณ มากน้อยเพียงใด โปรดเรียงตามลำดับ โดยไม่ซ้ำกัน [รีวิวจากบล็อกเกอร์สายกาแฟ เช่น บาริสต้า, Cafe hopper]': 'coffee_coffee_blogger',
        'บุคคลต่อไปนี้มีอิทธิพลในการซื้อกาแฟพร้อมดื่ม (Ready to drink) ของคุณ มากน้อยเพียงใด โปรดเรียงตามลำดับ โดยไม่ซ้ำกัน [รีวิวจากบล็อกเกอร์สายไลฟ์สไตล์/บันเทิง เช่น เทพลีลา]': 'coffee_lifestyle_blogger',
        'บุคคลต่อไปนี้มีอิทธิพลในการซื้อกาแฟพร้อมดื่ม (Ready to drink) ของคุณ มากน้อยเพียงใด โปรดเรียงตามลำดับ โดยไม่ซ้ำกัน [เพื่อน ครอบครัว และคนใกล้ตัว]': 'coffee_friends_family',
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
        'ในการดื่มชาพร้อมดื่ม (Ready to drink) คุณให้ความสำคัญกับคุณสมบัติด้านล่างนี้มากน้อยเพียงใด (5 = สำคัญมากที่สุด) [กลิ่นหอมใบชาเขียว]': 'tea_aroma',
        'ในการดื่มชาพร้อมดื่ม (Ready to drink) คุณให้ความสำคัญกับคุณสมบัติด้านล่างนี้มากน้อยเพียงใด (5 = สำคัญมากที่สุด) [รสชาติชาเขียวเข้มข้น]': 'tea_intensity',
        'ในการดื่มชาพร้อมดื่ม (Ready to drink) คุณให้ความสำคัญกับคุณสมบัติด้านล่างนี้มากน้อยเพียงใด (5 = สำคัญมากที่สุด) [ไม่เติมน้ำตาล/ไม่มีน้ำตาล]': 'tea_no_sugar',
        'ในการดื่มชาพร้อมดื่ม (Ready to drink) คุณให้ความสำคัญกับคุณสมบัติด้านล่างนี้มากน้อยเพียงใด (5 = สำคัญมากที่สุด) [ไม่มีแคลอรี่ (0 kcal)]': 'tea_zero_kcal',
        'ในการดื่มชาพร้อมดื่ม (Ready to drink) คุณให้ความสำคัญกับคุณสมบัติด้านล่างนี้มากน้อยเพียงใด (5 = สำคัญมากที่สุด) [มีฉลากเห็นข้อมูลโภชนาการ (Nutrition facts)]': 'tea_nutrition',
        'ในการดื่มชาพร้อมดื่ม (Ready to drink) คุณให้ความสำคัญกับคุณสมบัติด้านล่างนี้มากน้อยเพียงใด (5 = สำคัญมากที่สุด) [แหล่งที่มาของใบชา เช่น ญี่ปุ่น]': 'tea_origin',
        'ในการดื่มชาพร้อมดื่ม (Ready to drink) คุณให้ความสำคัญกับคุณสมบัติด้านล่างนี้มากน้อยเพียงใด (5 = สำคัญมากที่สุด) [วิธีการชง/สกัดชาเขียว เช่น สกัดเย็น]': 'tea_brewing',
        'ในการดื่มชาพร้อมดื่ม (Ready to drink) คุณให้ความสำคัญกับคุณสมบัติด้านล่างนี้มากน้อยเพียงใด (5 = สำคัญมากที่สุด) [ความสะดวก/พกพาง่าย/ไม่เลอะเทอะ]': 'tea_convenience',
        'ในการดื่มชาพร้อมดื่ม (Ready to drink) คุณให้ความสำคัญกับคุณสมบัติด้านล่างนี้มากน้อยเพียงใด (5 = สำคัญมากที่สุด) [แบรนด์ดัง น่าเชื่อถือ]': 'tea_brand_trust',
        'ในการดื่มชาพร้อมดื่ม (Ready to drink) คุณให้ความสำคัญกับคุณสมบัติด้านล่างนี้มากน้อยเพียงใด (5 = สำคัญมากที่สุด) [ภาพลักษณ์ดูดี ดูพรีเมียม]': 'tea_premium',
        'ในการดื่มชาพร้อมดื่ม (Ready to drink) คุณให้ความสำคัญกับคุณสมบัติด้านล่างนี้มากน้อยเพียงใด (5 = สำคัญมากที่สุด) [แพ็คเกจ/ขวดสวย]': 'tea_packaging',

        # อิทธิพลต่อการซื้อชา (Tea Influencers)
        'คุณรู้จักชาแบรนด์ใหม่จากที่สื่อบ้าง(เลือกได้หลายคำตอบ)': 'new_tea_discovery',
        'ถ้ามีแบรนด์ชาพร้อมดื่ม (Ready to drink) ออกใหม่ คุณจะลองหรือไม่': 'will_try_new_rtd_tea',
        'บุคคลต่อไปนี้มีอิทธิพลในการซื้อชาพร้อมดื่ม (Ready to drink) ของคุณ มากน้อยเพียงใด โปรดเรียงตามลำดับ โดยไม่ซ้ำกัน [รีวิวจากดารา]': 'tea_celebrity',
        'บุคคลต่อไปนี้มีอิทธิพลในการซื้อชาพร้อมดื่ม (Ready to drink) ของคุณ มากน้อยเพียงใด โปรดเรียงตามลำดับ โดยไม่ซ้ำกัน [รีวิวจากบล็อกเกอร์สายอาหารและเครื่องดื่ม เช่น กินหนม, ถนัดชิม]': 'tea_food_blogger',
        'บุคคลต่อไปนี้มีอิทธิพลในการซื้อชาพร้อมดื่ม (Ready to drink) ของคุณ มากน้อยเพียงใด โปรดเรียงตามลำดับ โดยไม่ซ้ำกัน [รีวิวจากบล็อกเกอร์สายสุขภาพ/สายคลีน]': 'tea_health_blogger',
        'บุคคลต่อไปนี้มีอิทธิพลในการซื้อชาพร้อมดื่ม (Ready to drink) ของคุณ มากน้อยเพียงใด โปรดเรียงตามลำดับ โดยไม่ซ้ำกัน [รีวิวจากบล็อกเกอร์สายไลฟ์สไตล์/บันเทิง เช่น เทพลีลา]': 'tea_lifestyle_blogger',
        'บุคคลต่อไปนี้มีอิทธิพลในการซื้อชาพร้อมดื่ม (Ready to drink) ของคุณ มากน้อยเพียงใด โปรดเรียงตามลำดับ โดยไม่ซ้ำกัน [เพื่อน ครอบครัว และคนใกล้ตัว]': 'tea_friends_family',
        'คุณซื้อชาพร้อมดื่ม (Ready to drink) จากช่องทางใดบ้าง': 'rtd_tea_purchase_channels'
    }
    df.rename(columns=col_map, inplace=True)

    # Save to JSON (Data Dictionary)
    with open('column_mapping.json', 'w', encoding='utf-8') as f:
        json.dump(col_map, f, ensure_ascii=False, indent=4)
    print("Dictionary has been saved as a 'column_mapping.json' file.")

    # Manage Datetime features
    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
    df['hour'] = df['timestamp'].dt.hour
    df['day_of_week'] = df['timestamp'].dt.day_name()
    df['month'] = df['timestamp'].dt.month_name()

    # Logic Check (age)
    if 'age' in df.columns:
        df['age'] = pd.to_numeric(df['age'], errors='coerce')
        df.loc[(df['age'] < 10) | (df['age'] > 100), 'age'] = np.nan

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
        'interests', 'ad_channels_seen', 'influence_ad', 'trusted_ad', 
        'tv_channels', 'top5_channels', 'tv_program_types', 'tv_platforms', 
        'ooh_types_seen', 'social_media_used', 'streaming_used', 
        'audio_streaming_used', 'coffee_types', 'rtd_coffee_brands', 
        'rtd_coffee_occasions', 'new_coffee_discovery', 
        'will_try_new_rtd_coffee', 'rtd_coffee_purchase_channels', 
        'tea_types', 'rtd_tea_brands', 'rtd_tea_occasions', 'new_tea_discovery',
        'will_try_new_rtd_tea', 'rtd_tea_purchase_channels'
    ]
    for col in multi_answer_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.replace(', ', ',', regex=False)

    # Manage Null for people who "ไม่ดื่ม" coffee/tea
    coffee_choice_cols = [
        'coffee_types', 'most_freq_coffee', 'most_freq_coffee_merged',
        'fav_coffee_type', 'rtd_coffee_brands', 'most_freq_rtd_brand',
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
        'coffee_fresh_taste', 'coffee_intensity', 'coffee_smooth', 'coffee_acidity',
        'coffee_aroma', 'coffee_caffeine', 'coffee_origin', 'coffee_convenience',
        'coffee_value', 'coffee_nutrition', 'coffee_brand_trust', 'coffee_premium',
        'coffee_packaging', 'tea_aroma', 'tea_intensity', 'tea_no_sugar', 
        'tea_zero_kcal', 'tea_nutrition', 'tea_origin', 'tea_brewing', 
        'tea_convenience', 'tea_brand_trust', 'tea_premium', 'tea_packaging'
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
        'coffee_celebrity', 'coffee_food_blogger',
        'coffee_coffee_blogger', 'coffee_lifestyle_blogger',
        'coffee_friends_family'
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
        'tea_celebrity', 'tea_food_blogger',
        'tea_health_blogger', 'tea_lifestyle_blogger',
        'tea_friends_family'
    ]
    for col in tea_influencer_cols:
        if col in df.columns:
            df[col] = df[col].replace(rating_mapping_tea_inf)

    # Standardization (คำถามปลายเปิด)
    if 'reason_like' in df.columns:
        df['reason_like'] = df['reason_like'].fillna('').astype(str)
        df['reason_like_category'] = 'อื่นๆ / ไม่ระบุ'

        df.loc[df['reason_like'].str.contains('รส|อร่อย|เข้ม|หอม', na=False), 'reason_like_category'] = 'รสชาติ'
        df.loc[df['reason_like'].str.contains('ราคา|ถูก|คุ้ม|คุณภาพ', na=False), 'reason_like_category'] = 'ราคา/ความคุ้มค่า'
        df.loc[df['reason_like'].str.contains('สาขา|สะดวก|หาง่าย|ปั๊ม', na=False), 'reason_like_category'] = 'ความสะดวก/สาขาเยอะ'
        df.loc[df['reason_like'].str.contains('โปร|ส่วนลด', na=False), 'reason_like_category'] = 'โปรโมชั่น'

    # Target Variable Identification & Labeling
    def segment_customer(row):
        if row.get('like_cafe_amazon') in ['ชอบ', 'ชอบดื่ม'] and row.get('will_try_new_rtd_coffee') in ['ลองแน่นอน', 'อาจจะลอง']:
            return 'Brand Loyalists (High Potential)'
        elif row.get('like_cafe_amazon') in ['ไม่ชอบ', 'ไม่ชอบดื่ม', 'เฉยๆ'] and row.get('will_try_new_rtd_coffee') in ['ลองแน่นอน', 'อาจจะลอง']:
            return 'New Potential Customers'
        elif row.get('like_cafe_amazon') in ['ชอบ', 'ใช่', 'ชอบดื่ม'] and row.get('will_try_new_rtd_coffee') in ['ไม่ลอง', 'ไม่แน่ใจ']:
            return 'Store-Only Loyalists'
        else:
            return 'General / Unlikely to buy'

    if 'like_cafe_amazon' in df.columns and 'will_try_new_rtd_coffee' in df.columns:
        df['customer_segment'] = df.apply(segment_customer, axis=1)

    return df

if __name__ == '__main__':
    try:
        raw_df = pd.read_csv('Case_3_Media_Behavior.csv')
        print(raw_df.shape)

        cleaned_df = clean_data(raw_df)
        print(f"Clean the data successfully!: {cleaned_df.shape}")
        
        print("\nExample of column name after clean: ")
        print(cleaned_df.columns.tolist()[:10])
        
    except FileNotFoundError:
        print("'Case_3_Media_Behavior.csv' file not found")
