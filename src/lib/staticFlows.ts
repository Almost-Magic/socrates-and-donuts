// 6 pre-written question flows, ~120 steps total

export type FlowType = 'decision' | 'anger' | 'hurt' | 'grief' | 'anxiety' | 'general';

interface FlowStep {
  question: string;
  followUp?: string;
}

interface Flow {
  entry: string;
  steps: FlowStep[];
}

export const flows: Record<FlowType, Flow> = {
  decision: {
    entry: "I need to make a decision",
    steps: [
      { question: "Before we look at the options, let's check in with your body. Where do you feel this decision right now? Chest? Head? Stomach?" },
      { question: "What's the quality of that sensation? Is it tight? Heavy? Restless? Calm?" },
      { question: "As you pay attention to it, is the sensation changing, or staying the same?" },
      { question: "Tell me about the decision you need to make. What are the options as you see them?" },
      { question: "What would the ideal outcome look like? Not what's realistic — what's ideal?" },
      { question: "Now, what's the worst case scenario for each option? Be specific." },
      { question: "What are you afraid might happen if you choose wrong?" },
      { question: "What would you do if you knew you couldn't fail?" },
      { question: "Looking back, have you faced a similar decision before? What happened?" },
      { question: "If a close friend were in your exact situation, what would you advise them to do?" },
      { question: "What does your body want to do? Not your mind — your body." },
      { question: "What would you do if you only had 24 hours to decide?" },
      { question: "What's the one thing you don't want to regret in five years?" },
      { question: "Is there information you're avoiding that might help clarify this?" },
      { question: "What would 'enough information' look like? Do you have it?" },
      { question: "Which option aligns most with who you want to become?" },
      { question: "What are you really choosing here — the outcome, or the path?" },
      { question: "If you chose perfectly, what would that look like? And can any choice actually be perfect?" },
      { question: "What's the kindest thing you can do for your future self?" },
      { question: "You've thought about this carefully. What's your intuition saying — even if it's not fully formed?" },
      { question: "What would it feel like to trust yourself either way?" },
      { question: "What would you do if you loved yourself completely?" },
      { question: "Is there a third option you haven't considered?" },
      { question: "Ready to decide? Remember: clarity doesn't guarantee perfection. You can adapt as you go." },
    ],
  },
  anger: {
    entry: "I'm angry and about to do something",
    steps: [
      { question: "Before we look at what happened, let's check in with your body. Where do you feel this anger right now? Chest? Jaw? Hands? Stomach?" },
      { question: "What's the quality of that sensation? Hot? Tight? Pulsing? Heavy?" },
      { question: "Is the sensation changing as you pay attention to it, or is it staying the same?" },
      { question: "Now tell me — what happened. Just the facts, like a news reporter. What did they actually do or say?" },
      { question: "And what's the story your mind is telling you about why they did it?" },
      { question: "Is there any other possible explanation for why they might have done this?" },
      { question: "What do you want to do right now? Be honest — what's the impulse?" },
      { question: "If you did that, what would happen in the next hour? Be specific." },
      { question: "And what about tomorrow morning? How would you feel about having done it?" },
      { question: "Here's the real question: what are you actually protecting? What feels threatened?" },
      { question: "When you were younger, did something similar happen that still sits with you?" },
      { question: "What would happen if you waited 24 hours before taking action?" },
      { question: "What are you really angry about — this incident, or something deeper?" },
      { question: "If you responded from a place of complete calm, what would you do differently?" },
      { question: "What outcome are you hoping for with your response? Is it realistic?" },
      { question: "What would the person you'd want to be do in this situation?" },
      { question: "Is there anything you're not seeing because the anger is loud?" },
      { question: "What would you say to someone else in this exact situation?" },
      { question: "The anger is giving you energy. What else could you do with it besides respond?" },
    ],
  },
  hurt: {
    entry: "I'm hurt and want to say something",
    steps: [
      { question: "Let's begin with your body. Where do you feel this hurt? Is it in your chest, throat, stomach somewhere else?" },
      { question: "What's the texture of the feeling? Is it sharp? Aching? Empty? Heavy?" },
      { question: "As you sit with it, does it shift at all, or does it stay fixed?" },
      { question: "Tell me what happened. Just the facts — no interpretation yet." },
      { question: "What did their words or actions mean to you? What did you hear them say?" },
      { question: "Is there any possibility they didn't intend to hurt you? What else might be true?" },
      { question: "What do you wish they had done or said instead?" },
      { question: "What are you afraid will happen if you don't express this?" },
      { question: "What are you afraid will happen if you do?" },
      { question: "If you spoke to them from a place of vulnerability rather than anger, what might you say?" },
      { question: "What do you need them to understand? Not to agree — to understand." },
      { question: "What would it look like to take care of yourself right now, regardless of their response?" },
      { question: "Is there something deeper this is bringing up for you?" },
      { question: "What would you do if you knew they cared but were bad at showing it?" },
      { question: "What do you need right now — to be heard, to be validated, to reconnect, or something else?" },
      { question: "Could you write them a letter you'll never send, just to get clear on what you feel?" },
      { question: "What would self-compassion look like in this moment?" },
      { question: "If you waited a week, would this feel different? How?" },
      { question: "What's the kindest thing you can do for yourself while you process this?" },
      { question: "What would you tell a friend who was hurting this much?" },
    ],
  },
  grief: {
    entry: "I'm sad and thinking of a big change",
    steps: [
      { question: "Let's begin in your body. Where do you feel this sadness? Sometimes grief lives in unexpected places — chest, throat, arms, eyes?" },
      { question: "What's it like there? Heavy? Hollow? Tight? Raw?" },
      { question: "If this feeling had a colour or shape, what would it be?" },
      { question: "Tell me what's happening. What's the situation you're facing?" },
      { question: "What are you losing or letting go of? Name it specifically." },
      { question: "What does this loss mean to you? What made it important?" },
      { question: "What are you afraid might happen if you let go?" },
      { question: "What are you hoping might be on the other side?" },
      { question: "Is there any part of you that feels relief, even a little? That's okay if there is." },
      { question: "What would letting go look like — not all at once, but gradually?" },
      { question: "What have you learned from this that you can carry forward?" },
      { question: "What would honouring this loss look like? How can you mark it properly?" },
      { question: "Who or what could support you through this transition?" },
      { question: "What would you tell someone you loved who was going through this?" },
      { question: "What small step could you take toward what's next?" },
      { question: "How do you want to feel when you've moved through this? What would that version of you look like?" },
      { question: "What can you do today to be gentle with yourself?" },
      { question: "Is there something you're not grieving that you should acknowledge?" },
      { question: "What would it feel like to make peace with what's happening?" },
      { question: "You've been carrying a lot. What do you need right now?" },
    ],
  },
  anxiety: {
    entry: "I'm anxious and stuck in my head",
    steps: [
      { question: "Let's start in your body. Where does the anxiety live? Chest? Stomach? Head? Is it scattered or localised?" },
      { question: "What's the quality of the sensation? Racing? Tight? Unsteady? Jumpy?" },
      { question: "If you put your attention on it gently, does it shift, or does it stay the same?" },
      { question: "Tell me what's on your mind. What's the worry, the thought, the scenario playing out?" },
      { question: "What are you afraid might happen? Be specific — what's the worst case you're imagining?" },
      { question: "How likely is that worst case, really? What are the actual odds based on your experience?" },
      { question: "What would you do if that fear came true? Walk me through it." },
      { question: "And if you survived that — and you would — what would you do next?" },
      { question: "Is there information you're missing that would help, or is this uncertainty itself the problem?" },
      { question: "What has helped you manage anxiety before? Anything at all, even something small." },
      { question: "What would you do if you weren't afraid?" },
      { question: "Who can you talk to? Sometimes anxiety shrinks when we share it." },
      { question: "What can you control in this situation? What can't you?" },
      { question: "What would you tell someone you loved who was anxious about the same thing?" },
      { question: "Is there something physical you could do — walk, stretch, breathe — that might shift your nervous system?" },
      { question: "What are you avoiding that the anxiety might be pointing you toward?" },
      { question: "What would accepting uncertainty look like today?" },
      { question: "Can you name three things you're grateful for right now? They can be small." },
      { question: "What would it feel like to be gentle with yourself while you're anxious?" },
      { question: "The anxiety is trying to protect you from something. What is it trying to protect you from?" },
    ],
  },
  general: {
    entry: "Something else is bothering me",
    steps: [
      { question: "Let's begin with your body. Where do you feel this? Just point to where the feeling lives." },
      { question: "What does it feel like there? Describe it as best you can." },
      { question: "Is this feeling familiar? Has it been here before?" },
      { question: "Tell me what's happening. What's going on in your world?" },
      { question: "What part of this situation feels most heavy right now?" },
      { question: "What are you assuming that might not be true?" },
      { question: "What would you do if you were completely clear about what you wanted?" },
      { question: "What are you afraid to see or admit?" },
      { question: "What would clarity look like? What would you see differently?" },
      { question: "What small thing could you do right now to take care of yourself?" },
      { question: "Who could you talk to about this? Even just to be heard?" },
      { question: "What would you do if you loved yourself through this completely?" },
      { question: "What is this experience trying to teach you?" },
      { question: "What have you learned from similar experiences before?" },
      { question: "What would you do if you knew you couldn't fail?" },
    ],
  },
};

export function getFlow(flowType: FlowType): Flow {
  return flows[flowType];
}

export function getNextQuestion(flowType: FlowType, stepIndex: number): string | null {
  const flow = flows[flowType];
  if (stepIndex >= flow.steps.length) {
    return null;
  }
  return flow.steps[stepIndex].question;
}

export function getTotalSteps(flowType: FlowType): number {
  return flows[flowType].steps.length;
}

export function getAllFlowTypes(): FlowType[] {
  return ['decision', 'anger', 'hurt', 'grief', 'anxiety', 'general'];
}
