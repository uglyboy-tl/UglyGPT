from uglygpt.chains.gen_image.base import ImageGeneratorChain
image_generator = ImageGeneratorChain.from_llm()
print(image_generator("原神中的霄宫"))