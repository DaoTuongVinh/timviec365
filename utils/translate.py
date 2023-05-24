# coding=utf-8

#import gradio as gr
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

dict_map = {
    "òa": "oà",
    "Òa": "Oà",
    "ÒA": "OÀ",
    "óa": "oá",
    "Óa": "Oá",
    "ÓA": "OÁ",
    "ỏa": "oả",
    "Ỏa": "Oả",
    "ỎA": "OẢ",
    "õa": "oã",
    "Õa": "Oã",
    "ÕA": "OÃ",
    "ọa": "oạ",
    "Ọa": "Oạ",
    "ỌA": "OẠ",
    "òe": "oè",
    "Òe": "Oè",
    "ÒE": "OÈ",
    "óe": "oé",
    "Óe": "Oé",
    "ÓE": "OÉ",
    "ỏe": "oẻ",
    "Ỏe": "Oẻ",
    "ỎE": "OẺ",
    "õe": "oẽ",
    "Õe": "Oẽ",
    "ÕE": "OẼ",
    "ọe": "oẹ",
    "Ọe": "Oẹ",
    "ỌE": "OẸ",
    "ùy": "uỳ",
    "Ùy": "Uỳ",
    "ÙY": "UỲ",
    "úy": "uý",
    "Úy": "Uý",
    "ÚY": "UÝ",
    "ủy": "uỷ",
    "Ủy": "Uỷ",
    "ỦY": "UỶ",
    "ũy": "uỹ",
    "Ũy": "Uỹ",
    "ŨY": "UỸ",
    "ụy": "uỵ",
    "Ụy": "Uỵ",
    "ỤY": "UỴ",
    }

tokenizer_vi2en = AutoTokenizer.from_pretrained("vinai/vinai-translate-vi2en", src_lang="vi_VN")
model_vi2en = AutoModelForSeq2SeqLM.from_pretrained("vinai/vinai-translate-vi2en")

def translate_vi2en(vi_text: str) -> str:
    for i, j in dict_map.items():
        vi_text = vi_text.replace(i, j)
    input_ids = tokenizer_vi2en(vi_text, return_tensors="pt").input_ids
    output_ids = model_vi2en.generate(
        input_ids,
        do_sample=True,
        top_k=100,
        top_p=0.8,
        decoder_start_token_id=tokenizer_vi2en.lang_code_to_id["en_XX"],
        num_return_sequences=1,
    )
    en_text = tokenizer_vi2en.batch_decode(output_ids, skip_special_tokens=True)
    en_text = " ".join(en_text)
    return en_text

tokenizer_en2vi = AutoTokenizer.from_pretrained("vinai/vinai-translate-en2vi", src_lang="en_XX")
model_en2vi = AutoModelForSeq2SeqLM.from_pretrained("vinai/vinai-translate-en2vi")

def translate_en2vi(en_text: str) -> str:
    input_ids = tokenizer_en2vi(en_text, return_tensors="pt").input_ids
    output_ids = model_en2vi.generate(
        input_ids,
        do_sample=True,
        top_k=100,
        top_p=0.8,
        decoder_start_token_id=tokenizer_en2vi.lang_code_to_id["vi_VN"],
        num_return_sequences=1,
    )
    vi_text = tokenizer_en2vi.batch_decode(output_ids, skip_special_tokens=True)
    vi_text = " ".join(vi_text)
    return vi_text

vi_example_text = ["Cô cho biết: trước giờ tôi không đến phòng tập công cộng, mà tập cùng giáo viên Yoga riêng hoặc tự tập ở nhà. Khi tập thể dục trong không gian riêng tư, tôi thoải mái dễ chịu hơn.",
                   "cô cho biết trước giờ tôi không đến phòng tập công cộng mà tập cùng giáo viên yoga riêng hoặc tự tập ở nhà khi tập thể dục trong không gian riêng tư tôi thoải mái dễ chịu hơn"]

en_example_text = ["I haven't been to a public gym before. When I exercise in a private space, I feel more comfortable.",
                   "i haven't been to a public gym before when i exercise in a private space i feel more comfortable"]

"""
with gr.Blocks() as demo:
    with gr.Tabs():
        with gr.TabItem("Vietnamese to English"):
            with gr.Row():
                with gr.Column():
                    vietnamese = gr.Textbox(label="Vietnamese Text")
                    translate_to_english = gr.Button(value="Translate To English")
                with gr.Column():
                    english = gr.Textbox(label="English Text")
            translate_to_english.click(lambda text: translate_vi2en(text), inputs=vietnamese, outputs=english)
            gr.Examples(examples=vi_example_text,
                        inputs=[vietnamese])

        with gr.TabItem("English to Vietnamese"):
            with gr.Row():
                with gr.Column():
                    english = gr.Textbox(label="English Text")
                    translate_to_vietnamese = gr.Button(value="Translate To Vietnamese")
                with gr.Column():
                    vietnamese = gr.Textbox(label="Vietnamese Text")
            translate_to_vietnamese.click(lambda text: translate_en2vi(text), inputs=english, outputs=vietnamese)
            gr.Examples(examples=en_example_text,
                        inputs=[english])
"""


if __name__ == "__main__":
    vi_text = translate_en2vi(en_example_text[0])
    print(vi_text)