from llm_sdk import Small_LLM_Model

model = Small_LLM_Model()
vocab_path = model.get_path_to_vocab_file()
# prompt = "Give me the correct and a straight answer (no workaround) to this question: What is the sum of 5 and 6?"
# input_ids = model.encode(prompt).tolist()[0]

# generated = ""
# for i in range(50):
#     logits = model.get_logits_from_input_ids(input_ids)
#     next_token = logits.index(max(logits))
#     generated += model.decode([next_token])
#     input_ids.append(next_token)

# print(generated)
print(vocab_path)