from urllib.parse import urlparse, parse_qs

from stqdm import stqdm

from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound

from transformers import pipeline
class InvalidURLException(Exception):
    pass

def get_videoid_from_url(url: str):
    url_data = urlparse(url)
    query = parse_qs(url_data.query)

    if ('v' in query) & ('youtube.com' in url_data.netloc):
        video_id = query["v"][0]
    elif 'youtu.be' in url_data.netloc:
        path_lst = url.split('/')

        if path_lst:
            video_id = path_lst[-1]
        else:
            raise InvalidURLException('Invalid URL')
    else:
        raise InvalidURLException('Invalid URL')

    return video_id


def get_transcripts(url: str):
    video_id = get_videoid_from_url(url)

    transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

    try:
        transcript = transcript_list.find_manually_created_transcript(['en'])
    except NoTranscriptFound as e:
        transcript = transcript_list.find_generated_transcript(['en'])

    subtitles = transcript.fetch()

    subtitles = [sbt['text'] for sbt in subtitles if sbt['text'] != '[Music]']

    return subtitles


def generate_summary(subtitles: list):
    subtitles_len = [len(sbt) for sbt in subtitles]
    sbt_mean_len = sum(subtitles_len) / len(subtitles_len)

    n_sbt_per_step = int(400 / (sbt_mean_len / 4))

    n_steps = len(subtitles) // n_sbt_per_step if len(subtitles) % n_sbt_per_step == 0 else \
        len(subtitles) // n_sbt_per_step + 1

    summaries = []

    for i in stqdm(range(n_steps)):
        sbt_txt = ' '.join(subtitles[n_sbt_per_step * i:n_sbt_per_step * (i + 1)])

        summarizer = pipeline('summarization', model='knkarthick/MEETING_SUMMARY')

        summary = summarizer(sbt_txt, do_sample=False)
        summary = summary[0]['summary_text']

        summaries.append(summary)

    return ' '.join(summaries)