# Healthcare-Chatbot (2021)

> Tools - RASA, Python, Twilio, WhatsApp, Ngrok, Infermedica and Google Maps API, SQLite

Engineered a chatbot in RASA which interacts in natural language and gathers a set of symptoms from the user and using an API from Infermedica, provides a diagnosis, along with a list of relevant doctors sorted by ratings, nearby hospitals, and pharmacies, with an overall confidence of 92-95% in identifying the user intents and performing entity-recognition

## About

This chatbot has been built from a demonstration point of view to exhibit the learnings imbibed from CS6120 Natural Language Processing, at Northeastern University. This bot has been developed to locate licensed hospitals, pharmacies for agiven area and return directions to the same on Google Maps. A framework of a symptom-checker has also been included in the project to aid in self-diagnosis. To achieve diagnostic results to symptoms provided by the user, calls were made to the APIs by a third-party provider. There is also a module in the project which lets a user view his insurance details, update the same or check the status of his claims. The chatbot assists by guiding patients/users to a set of possible underlying conditions. Users can converse with this bot through WhatsApp via Twilio as an intermediary.

## Architecture

<p align="center">
<img src="https://github.com/divitvasu/Healthcare-Chatbot/assets/30820920/8cb24a9c-626e-4246-bf24-68a7a8ff37e2" alt="Image" width="600" height="400">
</p>

## Sample Execution

- Insurance Checker Flow, showing three possible operations
<p align="center">
<img src="https://github.com/divitvasu/Healthcare-Chatbot/assets/30820920/2d09f3ed-9694-4761-bbd4-cc65a1080305" alt="Image" width="500" height="250">
</p>

<p align="center">
<img src="https://github.com/divitvasu/Healthcare-Chatbot/assets/30820920/06835abb-18d0-4a55-b243-8dfcade0afd9" alt="Image" width="500" height="250">
</p>

<p align="center">
<img src="https://github.com/divitvasu/Healthcare-Chatbot/assets/30820920/2e516108-aa98-4ac7-8c8a-34d9b5a1fd8c" alt="Image" width="500" height="250">
</p>

- A sample output from the terminal is as shown when the bot is being queried via WhatsApp. Once the action server and ngrok are running, the following command
needs to be run: 
`‘rasa run –m models –enable-api –cors “*” –debug’`. This will publish the rasa server on the localhost.

<p align="center">
<img src="https://github.com/divitvasu/Healthcare-Chatbot/assets/30820920/0d46bd30-c077-4dd9-9d4c-dda071afe8ac" alt="Image" width="600" height="800">
</p>

- Ngrok then guides the localhost path to the created Twilio webhook as below.

<p align="center">
<img src="https://github.com/divitvasu/Healthcare-Chatbot/assets/30820920/6625b52d-79da-4994-b365-97b859d85008" alt="Image" width="500" height="250">
</p>

- Execution samples on Whatsapp

<p align="center">
<img src="https://github.com/divitvasu/Healthcare-Chatbot/assets/30820920/0c1b2f0e-4d44-44e2-97ff-40160a5a669c" alt="Image" width="250" height="450">
</p>

<p align="center">
<img src="https://github.com/divitvasu/Healthcare-Chatbot/assets/30820920/92ea183b-79e3-46ad-9fc1-1793f264206d" alt="Image" width="300" height="300">
</p>

<p align="center">
<img src="https://github.com/divitvasu/Healthcare-Chatbot/assets/30820920/518dc8d7-4ab3-4807-954b-e198a05d51aa" alt="Image" width="300" height="400">
</p>

<p align="center">
<img src="https://github.com/divitvasu/Healthcare-Chatbot/assets/30820920/325405e4-e13b-46e8-a234-4748a9cc4253" alt="Image" width="300" height="400">
</p>

## Future Scope

The bot built is more aimed towards demonstrating purposes, thus, is not extensive in nature. *It is not meant to be a substitute for qualified healthcare professionals!* As future scope of this project, one could integrate these functionalities into one single bot with a symptom checker (As of now, there are two separate modules). A real-life application of the same could involve leveraging cloud services for computing. Also, the model can be made to train with real-time data from incoming user queries to make it more robust. This would require a lot of data pre-processing, pipelining and handling, but should be fun, nonetheless.
A rail-based path could also be provided as an option by incorporating the use of pre-defined buttons for sequential tasks. These sequential tasks could comprise appointment scheduling, showing FAQs etc. The bot could also be modelled to be used as a front-desk respondent at a hospital.

### References

* [AI Assistants in Healthcare: An Open-Source Starter Pack for Developers to Automate Full Conversations](https://blog.rasa.com/ai-assistants-in-healthcare-an-open-source-starter-pack-for-developers-to-automate-full-conversations)
* [Rasa Installation Guide](https://rasa.com/docs/rasa/user-guide/installation/)
* [Rasa Tutorial](https://rasa.com/docs/rasa/user-guide/rasa-tutorial/)
* [Create Chatbot using Rasa - Part 1](https://towardsdatascience.com/create-chatbot-using-rasa-part-1-67f68e89ddad)
* [Choosing a Pipeline in Rasa](https://rasa.com/docs/rasa/nlu/choosing-a-pipeline/)
* [Entity Extraction in Rasa](https://rasa.com/docs/rasa/nlu/entity-extraction/)
* [Rasa Masterclass Handbook - Episode 3](https://blog.rasa.com/the-rasa-masterclass-handbook-episode-3/)
* [Rasa NLU Components](https://rasa.com/docs/rasa/nlu/components/)
* [Rasa Masterclass Handbook - Episode 7](https://blog.rasa.com/the-rasa-masterclass-handbook-episode-7/)
* [Using Action Listen inside a Custom Action in Rasa](https://stackoverflow.com/questions/63700081/how-can-i-use-action-listen-inside-a-custom-action-in-rasa)
* [Google Places API Search Refinements](https://mapsplatform.googleblog.com/2012/05/google-places-api-search-refinements-as.html)

### Contributors
@ParshvaTimbadia
