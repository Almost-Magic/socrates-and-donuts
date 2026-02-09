// BesideYou Content Data
// Fork this file to create a version for your country or cancer type.
// All content is here — no hardcoded strings in the app.

const GLOSSARY = [
  {term:"Metastatic",def:"When cancer has spread from where it started to another part of the body. For example, breast cancer that spreads to the bones is still breast cancer, not bone cancer.",cat:"diagnosis"},
  {term:"Chemotherapy",def:"Treatment that uses medicines to kill cancer cells or stop them from growing. It can be given as a drip into a vein, as tablets, or sometimes as a cream. Tell your care team about any side effects — they can often help.",cat:"treatment"},
  {term:"Oncologist",def:"A doctor who specialises in treating cancer. There are different types: medical oncologists (medicines), radiation oncologists (radiation therapy), and surgical oncologists (surgery).",cat:"general"},
  {term:"Biopsy",def:"A small sample of tissue taken from your body to be looked at under a microscope. It helps doctors work out if cancer is present and what type it is.",cat:"procedures"},
  {term:"Radiation Therapy",def:"Treatment that uses high-energy rays (like X-rays) to kill cancer cells. It's usually targeted at the specific area where the cancer is. Also called radiotherapy.",cat:"treatment"},
  {term:"Staging",def:"Working out how far the cancer has spread. Stages are usually numbered 1 to 4, with stage 1 being the earliest. Staging helps your team plan the best treatment.",cat:"diagnosis"},
  {term:"Remission",def:"When cancer has reduced in size or is no longer detectable. Complete remission means no signs can be found. Partial remission means the cancer has shrunk but hasn't gone completely.",cat:"diagnosis"},
  {term:"Fatigue",def:"Extreme tiredness that doesn't get better with rest. It's one of the most common side effects of cancer treatment. Let your care team know — there may be things that can help.",cat:"side-effects"},
  {term:"Nausea",def:"Feeling sick to your stomach. Very common during chemotherapy. Anti-nausea medication can help a lot — don't hesitate to ask for it.",cat:"side-effects"},
  {term:"Immunotherapy",def:"Treatment that helps your own immune system recognise and fight cancer cells. It works differently from chemotherapy and can have different side effects.",cat:"treatment"},
  {term:"Palliative Care",def:"Care focused on improving quality of life and managing symptoms. Palliative care can be given alongside curative treatment — it's not just for end of life. It's about feeling as well as possible.",cat:"treatment"},
  {term:"Neutropenia",def:"When your white blood cell count is very low, making you more vulnerable to infections. Common during chemotherapy. Contact your care team immediately if you develop a fever.",cat:"side-effects"},
  {term:"CT Scan",def:"A scan that takes detailed pictures of the inside of your body using X-rays from different angles. You might need to drink a special liquid or have dye injected. It's painless but can feel a bit claustrophobic.",cat:"tests"},
  {term:"Tumour Marker",def:"Substances in the blood that can be higher when cancer is present. They're used to monitor how treatment is working, not usually to diagnose cancer on their own.",cat:"tests"},
  {term:"Lymph Nodes",def:"Small, bean-shaped organs that filter fluid and help fight infection. Cancer can sometimes spread to nearby lymph nodes. Your doctor may check them during diagnosis.",cat:"general"},
  {term:"MRI",def:"A scan that uses magnets and radio waves to create detailed pictures. No radiation is involved. It can be noisy — you'll usually be given earplugs or headphones.",cat:"tests"},
  {term:"PET Scan",def:"A scan that shows how active cells are in your body. Cancer cells are often more active. A small amount of radioactive sugar is injected — it's safe and leaves your body naturally.",cat:"tests"},
  {term:"Prognosis",def:"An estimate of how the cancer is likely to progress and respond to treatment. It's based on statistics and everyone's experience is different. Ask your doctor what this means for you specifically.",cat:"diagnosis"},
  {term:"Benign",def:"Not cancer. A benign tumour doesn't spread to other parts of the body. It may still need treatment if it's causing problems, but it's not cancerous.",cat:"diagnosis"},
  {term:"Malignant",def:"Cancerous. A malignant tumour can grow and spread to other parts of the body. This is what distinguishes cancer from benign growths.",cat:"diagnosis"},
  {term:"Neuropathy",def:"Numbness, tingling, or pain in the hands and feet. A common side effect of some chemotherapy drugs. Tell your care team — they may be able to adjust your treatment.",cat:"side-effects"},
  {term:"Infusion",def:"When medication is given slowly through a drip into a vein. Chemotherapy infusions can take anywhere from 30 minutes to several hours. Bring something to read or watch.",cat:"procedures"},
  {term:"Blood Count",def:"A blood test that measures different types of cells in your blood — red cells, white cells, and platelets. It's done regularly during treatment to check how your body is coping.",cat:"tests"},
  {term:"Adjuvant Therapy",def:"Treatment given after the main treatment (usually surgery) to lower the risk of cancer coming back. This might be chemotherapy, radiation, or hormone therapy.",cat:"treatment"},
  {term:"Neoadjuvant Therapy",def:"Treatment given before the main treatment (usually surgery) to shrink the tumour first. This can make surgery easier or more effective.",cat:"treatment"},
  {term:"Alopecia",def:"Hair loss. A common side effect of some chemotherapy drugs. Hair usually grows back after treatment ends. Ask about scalp cooling if this is a concern for you.",cat:"side-effects"},
  {term:"Mucositis",def:"Soreness, redness, or ulcers in the mouth and throat. Can make eating and drinking painful. Let your care team know — there are mouthwashes and medications that help.",cat:"side-effects"},
  {term:"Port-a-Cath",def:"A small device placed under the skin, usually in the chest, to make it easier to give chemotherapy and take blood. It means fewer needle sticks. Also called a port.",cat:"procedures"},
  {term:"PICC Line",def:"A thin tube inserted into a vein in your arm that reaches close to your heart. Used for giving chemotherapy or taking blood. It stays in for weeks or months.",cat:"procedures"},
  {term:"Oedema",def:"Swelling caused by fluid building up in body tissues. It can happen as a side effect of treatment or if lymph nodes have been removed. Gentle movement and compression can help.",cat:"side-effects"},
  {term:"Pathology",def:"The study of tissue samples to diagnose disease. After a biopsy, a pathologist examines the tissue under a microscope. The pathology report tells your team about the cancer.",cat:"tests"},
  {term:"Grading",def:"How different the cancer cells look compared to normal cells. Low grade (1) means the cells look more normal and tend to grow slowly. High grade (3) means they look very different and may grow faster.",cat:"diagnosis"},
  {term:"Hormone Therapy",def:"Treatment that blocks or lowers hormones that help some cancers grow. Used for cancers like breast and prostate that are hormone-sensitive. Given as tablets or injections.",cat:"treatment"},
  {term:"Targeted Therapy",def:"Treatment that targets specific features of cancer cells. Unlike chemotherapy, it's designed to affect cancer cells more than normal cells, which can mean fewer side effects.",cat:"treatment"},
  {term:"Clinical Trial",def:"A research study testing new treatments. Participation is voluntary and you can withdraw at any time. Ask your oncologist if there are any trials that might be suitable for you.",cat:"general"},
  {term:"Multidisciplinary Team",def:"A group of different health professionals who work together to plan your treatment. This usually includes surgeons, oncologists, nurses, and other specialists. Sometimes called an MDT.",cat:"general"},
  {term:"Scanxiety",def:"The anxiety and worry that comes before or while waiting for scan results. It's extremely common and completely normal. Talk to your care team or a counsellor if it's overwhelming.",cat:"general"},
  {term:"Survivorship",def:"Life after cancer treatment ends. It includes follow-up care, managing long-term effects, and adjusting to a new normal. Many hospitals have survivorship programs.",cat:"general"},
  {term:"Antiemetic",def:"Medication that prevents or reduces nausea and vomiting. Your care team will usually give you these before and after chemotherapy. Don't wait until you feel sick — take them as prescribed.",cat:"treatment"},
  {term:"Bone Marrow",def:"The soft tissue inside your bones that makes blood cells. Some cancers affect the bone marrow directly, and some treatments can temporarily reduce its ability to make new blood cells.",cat:"general"},
  {term:"Platelets",def:"Tiny blood cells that help your blood clot. Chemotherapy can lower your platelet count, making you bruise or bleed more easily. Your team monitors this with blood tests.",cat:"general"}
];

const RESOURCES = [
  {name:"Cancer Council Counselling",desc:"Free counselling for people affected by cancer. Available in person, by phone, or online.",cat:"emotional",who:"patients,carers",url:"https://www.cancer.org.au",phone:"13 11 20"},
  {name:"Look Good Feel Better",desc:"Free workshops helping people manage the appearance-related effects of cancer treatment.",cat:"practical",who:"patients",url:"https://lgfb.org.au"},
  {name:"Transport to Treatment",desc:"Help getting to and from cancer treatment appointments. Available through Cancer Council.",cat:"practical",who:"patients",url:"https://www.cancer.org.au"},
  {name:"Accommodation Assistance",desc:"Low-cost accommodation for people who need to travel for treatment.",cat:"practical",who:"patients,carers",url:"https://www.cancer.org.au"},
  {name:"Centrelink",desc:"Government support payments and services for people affected by cancer, including Sickness Allowance and Carer Payment.",cat:"financial",who:"patients,carers",url:"https://www.servicesaustralia.gov.au"},
  {name:"Cancer Council Financial Assistance",desc:"Grants and support for people experiencing financial hardship due to cancer.",cat:"financial",who:"patients,carers",url:"https://www.cancer.org.au"},
  {name:"Carer Gateway",desc:"Australian Government support for carers including respite, counselling, and practical assistance.",cat:"carer",who:"carers",url:"https://www.carergateway.gov.au",phone:"1800 422 737"},
  {name:"eviQ",desc:"Reliable, evidence-based cancer treatment information written for patients and their families.",cat:"medical",who:"patients,carers",url:"https://www.eviq.org.au"},
  {name:"Breast Cancer Network Australia",desc:"Support and information specifically for people affected by breast cancer.",cat:"medical",who:"patients,carers",url:"https://www.bcna.org.au"},
  {name:"Prostate Cancer Foundation",desc:"Support and information for people affected by prostate cancer.",cat:"medical",who:"patients,carers",url:"https://www.pcfa.org.au"},
  {name:"Leukaemia Foundation",desc:"Support for people with blood cancer including leukaemia, lymphoma, myeloma, and related disorders.",cat:"medical",who:"patients,carers",url:"https://www.leukaemia.org.au"},
  {name:"Canteen",desc:"Support for young people (12–25) affected by cancer — whether it's their own diagnosis or someone in their family.",cat:"emotional",who:"patients,carers",url:"https://www.canteen.org.au"},
  {name:"Camp Quality",desc:"Bringing optimism and fun to children (0–13) affected by cancer through camps, activities, and family support.",cat:"emotional",who:"patients,carers",url:"https://www.campquality.org.au"},
  {name:"Cancer Council Online Community",desc:"Connect with other people going through cancer in a safe, moderated online space.",cat:"emotional",who:"patients,carers",url:"https://onlinecommunity.cancer.org.au"},
  {name:"Peter MacCallum Cancer Centre",desc:"Australia's only public hospital solely dedicated to cancer treatment, research and education.",cat:"medical",who:"patients",url:"https://www.petermac.org"},
  {name:"Redkite",desc:"Financial, educational, and emotional support for families of children with cancer.",cat:"financial",who:"carers",url:"https://www.redkite.org.au"},
  {name:"National Disability Insurance Scheme (NDIS)",desc:"May provide support if cancer treatment has resulted in a permanent and significant disability.",cat:"financial",who:"patients",url:"https://www.ndis.gov.au"}
];

// Crisis numbers — first thing to localise for a different country
const CRISIS = {
  emergency: {number:"000",label:"Call 000 Now"},
  lines: [
    {name:"Lifeline",number:"13 11 14",tel:"131114",desc:"24/7 crisis support and suicide prevention. Someone is always there to listen."},
    {name:"Cancer Council Helpline",number:"13 11 20",tel:"131120",desc:"Free, confidential support from cancer nurses."},
    {name:"Beyond Blue",number:"1300 22 4636",tel:"1300224636",desc:"24/7 support for anxiety, depression, and emotional wellbeing."}
  ]
};
