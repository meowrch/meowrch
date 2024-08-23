lang=$(hyprctl devices -j | jq -r '.keyboards.[] | select(.main == true).active_keymap | 
  {
    "English (US)": "EN",
    "Russian": "RU",
    "French": "FR",
    "German": "DE",
    "Spanish": "ES",
    "Italian": "IT",
    "Portuguese": "PT",
    "Dutch": "NL",
    "Swedish": "SV",
    "Norwegian": "NO",
    "Danish": "DA",
    "Finnish": "FI",
    "Polish": "PL",
    "Czech": "CS",
    "Hungarian": "HU",
    "Greek": "EL",
    "Turkish": "TR",
    "Hebrew": "HE",
    "Arabic": "AR",
    "Thai": "TH",
    "Chinese (Simplified)": "ZH-CN",
    "Chinese (Traditional)": "ZH-TW",
    "Japanese": "JA",
    "Korean": "KO"
  }[.]')
  echo $lang
