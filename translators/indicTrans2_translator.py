import torch
from huggingface_hub import login
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
from IndicTransToolkit import IndicProcessor


class IndicTrans2Translator:
    def __init__(
        self,
        model_name="ai4bharat/indictrans2-indic-en-1B",
        device=None,
        hf_token=None,
    ):
        """
        Initialize IndicTrans2 translator.

        Args:
            model_name (str): HuggingFace model name
            device (str | None): 'cuda' or 'cpu'. Auto-detected if None
            hf_token (str | None): HuggingFace token (optional)
        """

        if hf_token:
            login(token=hf_token)

        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")

        self.tokenizer = AutoTokenizer.from_pretrained(
            model_name,
            trust_remote_code=True
        )

        self.model = AutoModelForSeq2SeqLM.from_pretrained(
            model_name,
            trust_remote_code=True
        ).to(self.device)

        self.model.eval()

        self.ip = IndicProcessor(inference=True)

    def translate(
        self,
        text,
        src_lang="hin_Deva",
        tgt_lang="eng_Latn",
        max_length=256,
        num_beams=5,
    ):
        """
        Translate Indic text to target language.

        Args:
            text (str | list[str]): Input text
            src_lang (str): Source language code
            tgt_lang (str): Target language code
            max_length (int): Max generation length
            num_beams (int): Beam search size

        Returns:
            str | list[str]: Translated text
        """
        single_input = isinstance(text, str)
        sentences = [text] if single_input else text

        # Preprocess
        batch = self.ip.preprocess_batch(
            sentences,
            src_lang=src_lang,
            tgt_lang=tgt_lang,
        )

        # Tokenize
        inputs = self.tokenizer(
            batch,
            truncation=True,
            padding="longest",
            return_tensors="pt",
            return_attention_mask=True,
        ).to(self.device)

        # Generate
        with torch.no_grad():
            generated_tokens = self.model.generate(
                **inputs,
                use_cache=True,
                max_length=max_length,
                num_beams=num_beams,
                num_return_sequences=1,
            )

        # Decode
        with self.tokenizer.as_target_tokenizer():
            decoded = self.tokenizer.batch_decode(
                generated_tokens.detach().cpu(),
                skip_special_tokens=True,
                clean_up_tokenization_spaces=True,
            )

        # Postprocess
        translations = self.ip.postprocess_batch(decoded, lang=tgt_lang)
        return translations[0] if single_input else translations
