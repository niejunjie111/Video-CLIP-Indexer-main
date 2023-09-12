import sys
import streamlit as st
from helper import search_frame
import os, shutil
from docarray import Document
import asyncio
import nest_asyncio
import time
import os
nest_asyncio.apply()

st.set_page_config(page_title='Video Retrieval', page_icon='🔍')
st.title('Video Retrieval')
uploaded_file = st.file_uploader('upload to file')
query = st.text_input('keyword', '')
# query='cat'
top_n = '5'
similarity_threshold = '0.15'   
cas_url = 'grpc://127.0.0.1:51000'
token = 'd8a7e2026bd16588029a6d3e94417ef6'
keyframes=[]
search_button = st.button('Search')

# async def func_1(i,d):
#     if i in d.tags['keyframe_indices']:
#         keyframe = Document(tensor=d.tensor[i],
#                             tags={'index': len(keyframes)})
#         keyframe.convert_image_tensor_to_blob()
#         keyframes.append(keyframe)
#     st.session_state.keyframes = keyframes
#     pass

# async def func_2(i,video,tags,scores):
#         # await asyncio.sleep(0.1)
#         index = int(tags[i]['index'])
#         start_index = video.tags['keyframe_indices'][index]
#         end_index = len(video.tensor) if index == len(
#             video.tags['keyframe_indices']) - 1 else \
#         video.tags['keyframe_indices'][index + 1]
#         similar_scene = Document(tensor=video.tensor[start_index: end_index])
#         similarity_score = scores[i]
#         if similarity_score >= float(similarity_threshold):
#             os.makedirs('tmp_videos', exist_ok=True)
#             similar_scene.save_video_tensor_to_file(
#                 file='tmp_videos/tmp.mp4')
#             st.text(
#                 f'Top {i + 1} match -- similarity score: {similarity_score}')
#             st.video('tmp_videos/tmp.mp4')#展示的片段
#             os.remove('tmp_videos/tmp.mp4')


async def start():
    if search_button:
        # 抽帧
        #读取视频
        with st.spinner('Please Wait , We are extracting key frames...'):
            os.makedirs('tmp_videos', exist_ok=True)

            with open('tmp_videos/' + uploaded_file.name, 'wb') as f:
                f.write(uploaded_file.getvalue())
            d = Document(uri='./tmp_videos/'+ uploaded_file.name).load_uri_to_video_tensor()
            st.session_state.original_video = d
            start_time = time.time() 

            tasks=[]
            for i in range(len(d.tensor)):
                if i in d.tags['keyframe_indices']:
                    keyframe = Document(tensor=d.tensor[i],
                                        tags={'index': len(keyframes)})
                    keyframe.convert_image_tensor_to_blob()
                    keyframes.append(keyframe)
                st.session_state.keyframes = keyframes

            #     tasks.append(asyncio.create_task(func_1(i,d))) 
            # loop=asyncio.get_event_loop()
            # loop.run_until_complete(asyncio.wait(tasks))
            
            end_time = time.time()
            run_time = end_time - start_time    # 程序的运行时间，单位为秒
            print(run_time)
    
        #识别
        if 'keyframes' in st.session_state and 'original_video' in st.session_state:
            video = st.session_state.original_video
            with st.spinner(f"Loading , We are searching from {len(st.session_state.keyframes)} keyframes..."):
                tags, id, scores = search_frame(st.session_state.keyframes,
                                                query, int(top_n),
                                                cas_url, token)
                max_similarity_score = scores[0]
                if max_similarity_score < float(similarity_threshold):
                    st.success(
                        f'No match found. Max similarity score: {max_similarity_score} '
                        f'is smaller than threshold: {similarity_threshold}')
                tasks2=[]
                start_time = time.time() 
                # for i in range(len(id)):
                #     tasks2.append(asyncio.create_task(func_2(i,video,tags,scores)))
                # loop=asyncio.get_event_loop()
                # loop.run_until_complete(asyncio.wait(tasks2))

                

                for i in range(len(id)):
                    index = int(tags[i]['index'])
                    start_index = video.tags['keyframe_indices'][index]
                    end_index = len(video.tensor) if index == len(
                        video.tags['keyframe_indices']) - 1 else \
                    video.tags['keyframe_indices'][index + 1]
    
                    similar_scene = Document(tensor=video.tensor[start_index: end_index])
                    similarity_score = scores[i]
    
                    if similarity_score >= float(similarity_threshold):
                        os.makedirs('tmp_videos', exist_ok=True)
                        similar_scene.save_video_tensor_to_file(
                            file='tmp_videos/tmp.mp4')
                        st.text(
                            f'Top {i + 1} match -- similarity score: {similarity_score}')
                        st.video('tmp_videos/tmp.mp4')#展示的片段
                        os.remove('tmp_videos/tmp.mp4')

                end_time = time.time()
                run_time = end_time - start_time    # 程序的运行时间，单位为秒
                print(run_time)
        else:
            st.warning('Please extract the key frame first')


if __name__=='__main__':
    asyncio.run(start())






