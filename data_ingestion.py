import tiktoken
from uglygpt import config, logger
from uglygpt.ingestion.document_loaders.text_loader import TextLoader
from uglygpt.text_splitter import RecursiveCharacterTextSplitter
from uglygpt.indexes import get_memory

def main() -> None:
    filename = 'test.txt'
    memory = get_memory(config, init=True)
    max_length = 2500
    overlap = 200

    """
    Ingest a file by reading its content, splitting it into chunks with a specified
    maximum length and overlap, and adding the chunks to the memory storage.

    :param filename: The name of the file to ingest
    :param memory: An object with an add() method to store the chunks in memory
    :param max_length: The maximum length of each chunk, default is 4000
    :param overlap: The number of overlapping characters between chunks, default is 200
    """
    try:
        logger.info(f"Working with file {filename}")
        content = TextLoader(filename).load()
        content_length = len(content)
        logger.warn(f"File length: {content_length} characters")
        enc = tiktoken.encoding_for_model("text-davinci-003")
        def _tiktoken_encoder(text: str) -> int:
            return len(
                enc.encode(
                    text
                )
            )
        splitter = RecursiveCharacterTextSplitter(
            separators=["\n", "。", "？", "！", "，", "；", "：", "、"],
            chunk_size=max_length,
            chunk_overlap=overlap,
            length_function=_tiktoken_encoder,
        )
        chunks = list(splitter.split_text(content))

        num_chunks = len(chunks)
        for i, chunk in enumerate(chunks):
            logger.info(f"Ingesting chunk {i + 1} / {num_chunks} into memory")
            """ memory_to_add = (
                f"Filename: {filename}\n" f"Content part#{i + 1}/{num_chunks}: {chunk}"
            ) """
            metadata = {"filename":filename, "index":f"{i+1}/{num_chunks}"}
            memory.add(chunk, metadata=metadata)

        logger.info(f"Done ingesting {num_chunks} chunks from {filename}.")
    except Exception as e:
        logger.error(f"Error while ingesting file '{filename}': {str(e)}")

if __name__ == "__main__":
    main()