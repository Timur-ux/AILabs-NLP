from typing import List
import fastapi
import ollama
import os
from pydantic import BaseModel
import json
import re

url = os.getenv("OLLAMA_URL")
if url is None:
    url = "http://localhost:11434"

ollamaClient = ollama.AsyncClient(host=url)

app = fastapi.FastAPI(docs_url="/docs")


class PreferredOutput(BaseModel):
    verdict: int
    reasoning: str

async def DoChatRequest(message: str, output=PreferredOutput.model_json_schema()):
    response = await ollamaClient.generate(model="qwen2.5:0.5b", prompt=message, format=output, options={
        "temperature": 1
    })
    content =  response["response"]
    content = re.sub(r"```json", "", content)
    content = re.sub(r"}```.*", "}", content)
    content = re.sub(r"```", "", content)
    content = json.loads(content)
    if(content["reasoning"] is list):
        for i, reason in enumerate(content["reasoning"]):
            content["reasoning"][i] = re.sub(r'[^\\]"', r'\\"', reason)
        
    return json.dumps(content)

class Data(BaseModel):
    message: str
@app.post("/AskOllama")
async def AskOllama(data: Data):
    return await DoChatRequest(data.message)

zeroShotPrompt='Check whether following email message is spam or not spam: \'{}\'. Output must be in plain JSON format with 2 fields. First must be "verdict" with value 1 if message is spam or 0 if it is not. Second must be "reasoning" with describing why you decide mark message as spam or not spam.'
@app.post("/zero-shot")
async def ZeroShot(data: Data):
    return await DoChatRequest(zeroShotPrompt.format(data.message))
    

class CoTOutput(BaseModel):
    verdict: int
    reasoning: List[str]

coTPrompt='''
You are spam checker. You need to process messages and check whether it is spam or not.

Produce output in JSON format like:
{{
    "verdict": number,
    "reasoning": string[]
}}

verdict must be 1 if you think that message is spam and 0 otherwise.
reasoning must be list of you thoughts that you use to create verdict.

Before do verdict think step by step and place you thoughts in "reasoning" field

Message to check: '{}'
'''
@app.post("/cot")
async def CoT(data: Data):
    message = coTPrompt.format(data.message)
    return await DoChatRequest(message, None)


fewShotPrompt = '''
You are spam checker. You need to process messages and check whether it is spam or not.

Produce output in JSON format like:
{{
    "verdict": number,
    "reasoning": string[]
}}

verdict must be 1 if you think that message is spam and 0 otherwise.
reasoning must be list of you thoughts that you use to create verdict.

Example: "martin a posted tassos papadopoulos the greek sculptor behind the plan judged that the limestone of mount kerdylio NUMBER miles east of salonika and not far from the mount athos monastic community was ideal for the patriotic sculpture as well as alexander s granite features NUMBER ft high and NUMBER ft wide a museum a restored amphitheatre and car park for admiring crowds are planned so is this mountain limestone or granite if it s limestone it ll weather pretty fast yahoo groups sponsor NUMBER dvds free s p join now URL to unsubscribe from this group send an email to forteana unsubscribe URL your use of yahoo groups is subject to URL" 
Answer: {{"verdict": 0, "reasoning": [ "The message does not contain any spam indicators.", "The message appears to be about a sculpture project, which is generally considered non-spam." ]}}

Example: "note this is not spam this is not unsolicited email you are receiving this message because you opted in to receive certain special offers from one of our partnering sites have you changed your mind do you want to stop receiving these special offers if so go down to the bottom and click on the unsubscribe link to be removed from this opt in only list dear subscriber please take a moment to remove yourself from this list if you feel you are receiving these messages in error by going down to the bottom and clicking on the unsubscribe link below special offer NUMBER NUMBER until NUMBER NUMBER NUMBER NUMBER NUMBER pm NUMBER sexual fitness and penis enlargement system video of the week choking a chinese chicken caught on tape some asian guy in a chinese dressing room what the hell is this guy doing in there is he actually chocking his chicken on tape you ll see about him and more when you check out this special offer offer NUMBER NUMBER NUMBER NUMBER page NUMBER of NUMBER special offer NUMBER NUMBER until NUMBER NUMBER NUMBER NUMBER NUMBER pm subject male enlargement strengthening and total sexual fitness for only NUMBER NUMBER just wanted to remind you about the special we have this month our total program has the following information how to increase permanent length how to increase permanent width how to stop pre mature ejaculation how to stop erectile dysfunction how to increase penis strength how to make your penis thick and meaty how to enlarge the penis head glans how to increase staying power how to increase ejaculation distance and volume plus much more plus our new quick start program quick start extreme sexual fitness program now you can jump start your penis enlargement and sexual fitness by using our quick start program the quick start program is a no frills bare bones sexual fitness and penis enlargement cram course set up to have you gaining size and performing better in a really short amount of time once you finish the quick start program you can explore the whole penis enlargement course using the quick start program is totally your option video library search our video library of instructional and original amateur entertainment videos inside the most information about penis enlargement and sexual fitness with over NUMBER different techniques each explained step by step this system is the best value for your money pound for pound the lowest price on the net NUMBER NUMBER for everything this offer is for a limited time only order today special offer NUMBER NUMBER until NUMBER NUMBER NUMBER NUMBER NUMBER pm for other info faq s testimonials ordering info business opps video of the week info advertising info plus all other go to URL NUMBER boost your sales your ad will be here if you want it seen by millions every month plus be in widely circulated magazines and newspapers nationwide plus join our permission based email advertising ring blow your sales through the roof ask us how at sales URL numbers NUMBER NUMBER coming soon have you changed your mind do you want to stop receiving these special offers if so go down to the bottom and click on the unsubscribe link to be removed from this opt in only list to remove yourself from further mailings click the link below URL"
Answer: {{"verdict" : 1, "reasoning": [ 
    "The message is not spam because it contains a clear call-to-action (CTA) for users to unsubscribe and stop receiving special offers.",
    "The message does not contain any unsolicited or promotional content that would be considered spam.",
    "The user has opted in to receive certain special offers from one of their partnering sites, which aligns with the definition of spam."
]}}

Example: "on fri NUMBER aug NUMBER robert harley wrote next time i hear a joke i promise not to laugh until i have checked out primary sources for confirmation in triplicate ok oh please walking sideways like that is bad for your shoes though it is kinda cute when you get all reasonomatic bang bang have a nice day URL"
Answer: "{{"verdict": 0, "reasoning": [
    "The message contains no explicit or implicit spam indicators.",
    "The content appears to be a casual joke about walking sideways, which is not typically associated with being rude or disrespectful."
]}}

Example: "all is it just me or has there been a massive increase in the amount of email being falsely bounced around the place i ve already received email from a number of people i don t know asking why i am sending them email these can be explained by servers from russia and elsewhere coupled with the false emails i received myself it s really starting to annoy me am i the only one seeing an increase in recent weeks martin martin whelan déise design URL tel NUMBER NUMBER our core product déiseditor allows organisations to publish information to their web site in a fast and cost effective manner there is no need for a full time web developer as the site can be easily updated by the organisations own staff instant updates to keep site information fresh sites which are updated regularly bring users back visit URL for a demonstration déiseditor managing your information _______________________________________________ iiu mailing list iiu URL URL"
Answer: "{{"verdict": 0, "reasoning": [
    "The message contains multiple complaints and requests, such as 'false emails', 'servers from Russia', 'false emails', 'impossible to update the site regularly'. These are not typical spam messages.",
    "The message is repetitive and does not provide any specific information or solutions. It seems like a complaint about receiving false emails instead of an actual problem.",
    "The sender's name, email address, and URL do not appear to be associated with any known spam addresses."
]}}

Example: "{}"
Answer: 
'''
@app.post("/few-shot")
async def FewShot(data: Data):
    message = fewShotPrompt.format(data.message)
    return await DoChatRequest(message, None)

coTFewShotPrompt = '''
You are spam checker. You need to process messages and check whether it is spam or not.

Produce output in JSON format like:
{{
    "verdict": number,
    "reasoning": string[]
}}

verdict must be 1 if you think that message is spam and 0 otherwise.
reasoning must be list of you thoughts that you use to create verdict.


Example: "martin a posted tassos papadopoulos the greek sculptor behind the plan judged that the limestone of mount kerdylio NUMBER miles east of salonika and not far from the mount athos monastic community was ideal for the patriotic sculpture as well as alexander s granite features NUMBER ft high and NUMBER ft wide a museum a restored amphitheatre and car park for admiring crowds are planned so is this mountain limestone or granite if it s limestone it ll weather pretty fast yahoo groups sponsor NUMBER dvds free s p join now URL to unsubscribe from this group send an email to forteana unsubscribe URL your use of yahoo groups is subject to URL" 
Answer: {{"verdict": 0, "reasoning": [ "The message does not contain any spam indicators.", "The message appears to be about a sculpture project, which is generally considered non-spam." ]}}

Example: "note this is not spam this is not unsolicited email you are receiving this message because you opted in to receive certain special offers from one of our partnering sites have you changed your mind do you want to stop receiving these special offers if so go down to the bottom and click on the unsubscribe link to be removed from this opt in only list dear subscriber please take a moment to remove yourself from this list if you feel you are receiving these messages in error by going down to the bottom and clicking on the unsubscribe link below special offer NUMBER NUMBER until NUMBER NUMBER NUMBER NUMBER NUMBER pm NUMBER sexual fitness and penis enlargement system video of the week choking a chinese chicken caught on tape some asian guy in a chinese dressing room what the hell is this guy doing in there is he actually chocking his chicken on tape you ll see about him and more when you check out this special offer offer NUMBER NUMBER NUMBER NUMBER page NUMBER of NUMBER special offer NUMBER NUMBER until NUMBER NUMBER NUMBER NUMBER NUMBER pm subject male enlargement strengthening and total sexual fitness for only NUMBER NUMBER just wanted to remind you about the special we have this month our total program has the following information how to increase permanent length how to increase permanent width how to stop pre mature ejaculation how to stop erectile dysfunction how to increase penis strength how to make your penis thick and meaty how to enlarge the penis head glans how to increase staying power how to increase ejaculation distance and volume plus much more plus our new quick start program quick start extreme sexual fitness program now you can jump start your penis enlargement and sexual fitness by using our quick start program the quick start program is a no frills bare bones sexual fitness and penis enlargement cram course set up to have you gaining size and performing better in a really short amount of time once you finish the quick start program you can explore the whole penis enlargement course using the quick start program is totally your option video library search our video library of instructional and original amateur entertainment videos inside the most information about penis enlargement and sexual fitness with over NUMBER different techniques each explained step by step this system is the best value for your money pound for pound the lowest price on the net NUMBER NUMBER for everything this offer is for a limited time only order today special offer NUMBER NUMBER until NUMBER NUMBER NUMBER NUMBER NUMBER pm for other info faq s testimonials ordering info business opps video of the week info advertising info plus all other go to URL NUMBER boost your sales your ad will be here if you want it seen by millions every month plus be in widely circulated magazines and newspapers nationwide plus join our permission based email advertising ring blow your sales through the roof ask us how at sales URL numbers NUMBER NUMBER coming soon have you changed your mind do you want to stop receiving these special offers if so go down to the bottom and click on the unsubscribe link to be removed from this opt in only list to remove yourself from further mailings click the link below URL"
Answer: {{"verdict" : 1, "reasoning": [ 
    "The message is not spam because it contains a clear call-to-action (CTA) for users to unsubscribe and stop receiving special offers.",
    "The message does not contain any unsolicited or promotional content that would be considered spam.",
    "The user has opted in to receive certain special offers from one of their partnering sites, which aligns with the definition of spam."
]}}

Example: "on fri NUMBER aug NUMBER robert harley wrote next time i hear a joke i promise not to laugh until i have checked out primary sources for confirmation in triplicate ok oh please walking sideways like that is bad for your shoes though it is kinda cute when you get all reasonomatic bang bang have a nice day URL"
Answer: "{{"verdict": 0, "reasoning": [
    "The message contains no explicit or implicit spam indicators.",
    "The content appears to be a casual joke about walking sideways, which is not typically associated with being rude or disrespectful."
]}}

Example: "all is it just me or has there been a massive increase in the amount of email being falsely bounced around the place i ve already received email from a number of people i don t know asking why i am sending them email these can be explained by servers from russia and elsewhere coupled with the false emails i received myself it s really starting to annoy me am i the only one seeing an increase in recent weeks martin martin whelan déise design URL tel NUMBER NUMBER our core product déiseditor allows organisations to publish information to their web site in a fast and cost effective manner there is no need for a full time web developer as the site can be easily updated by the organisations own staff instant updates to keep site information fresh sites which are updated regularly bring users back visit URL for a demonstration déiseditor managing your information _______________________________________________ iiu mailing list iiu URL URL"
Answer: "{{"verdict": 0, "reasoning": [
    "The message contains multiple complaints and requests, such as 'false emails', 'servers from Russia', 'false emails', 'impossible to update the site regularly'. These are not typical spam messages.",
    "The message is repetitive and does not provide any specific information or solutions. It seems like a complaint about receiving false emails instead of an actual problem.",
    "The sender's name, email address, and URL do not appear to be associated with any known spam addresses."
]}}

Before verdict think step by step and place you thoughts in "reasoning" field

Example: "{}"
Answer: 
'''
@app.post("/cot-few-shot")
async def CotFewShot(data: Data):
    message = coTFewShotPrompt.format(data.message)
    return await DoChatRequest(message, None)
