import os
import re
import sys
import threading
import urllib.request
import webbrowser

import customtkinter as ctk
from PIL import Image
from customtkinter import filedialog as fd
from pytube import Search, YouTube, exceptions, Playlist

from assets.CTkMessagebox import CTkMessagebox

CURRENT_PATH = os.path.dirname(os.path.realpath(__file__))
FONTS = {
    "title": ("", 24, "bold"),
    "subtitle": ("", 18, "normal"),
    "large": ("", 16, "normal"),
    "normal": ("", 14, "normal"),
    "small": ("", 12, "normal")
}
ICONS = {
    "close": ctk.CTkImage(Image.open(f"{CURRENT_PATH}\\assets\\icons\\close_black.png"),
                          Image.open(f"{CURRENT_PATH}\\assets\\icons\\close_white.png"), (24, 24)),
    "not_found": ctk.CTkImage(Image.open(f"{CURRENT_PATH}\\assets\\icons\\not_found.png"),
                              Image.open(f"{CURRENT_PATH}\\assets\\icons\\not_found.png"), (60, 60)),

    "one": ctk.CTkImage(Image.open(f"{CURRENT_PATH}\\assets\\icons\\1_black.png"),
                        Image.open(f"{CURRENT_PATH}\\assets\\icons\\1_white.png"), (24, 24)),
    "two": ctk.CTkImage(Image.open(f"{CURRENT_PATH}\\assets\\icons\\2_black.png"),
                        Image.open(f"{CURRENT_PATH}\\assets\\icons\\2_white.png"), (24, 24)),
    "three": ctk.CTkImage(Image.open(f"{CURRENT_PATH}\\assets\\icons\\3_black.png"),
                          Image.open(f"{CURRENT_PATH}\\assets\\icons\\3_white.png"), (24, 24)),

    "paste": ctk.CTkImage(Image.open(f"{CURRENT_PATH}\\assets\\icons\\paste.png"),
                          Image.open(f"{CURRENT_PATH}\\assets\\icons\\paste.png"), (70, 70)),
    "videos": ctk.CTkImage(Image.open(f"{CURRENT_PATH}\\assets\\icons\\videos.png"),
                           Image.open(f"{CURRENT_PATH}\\assets\\icons\\videos.png"), (70, 70)),
    "download": ctk.CTkImage(Image.open(f"{CURRENT_PATH}\\assets\\icons\\download.png"),
                             Image.open(f"{CURRENT_PATH}\\assets\\icons\\download.png"), (70, 70)),

    "video": ctk.CTkImage(Image.open(f"{CURRENT_PATH}\\assets\\icons\\video.png"),
                          Image.open(f"{CURRENT_PATH}\\assets\\icons\\video.png"), (60, 60)),
    "playlist": ctk.CTkImage(Image.open(f"{CURRENT_PATH}\\assets\\icons\\playlist.png"),
                             Image.open(f"{CURRENT_PATH}\\assets\\icons\\playlist.png"), (60, 60)),
}
LOGO = f"{CURRENT_PATH}\\assets\\icons\\logo.ico"
ctk.set_default_color_theme(f"{CURRENT_PATH}\\assets\\theme.json")


def on_close():
    app.destroy()
    try:
        os.remove(f"{CURRENT_PATH}\\assets\\downloads\\thumbnail.jpg")
    except (FileNotFoundError, PermissionError):
        pass
    sys.exit()


def sanitize_filename(filename):
    filename = re.sub(r'[\\/*?:"<>|]', "", filename)

    if len(filename) > 255:
        filename = filename[:255]

    return filename


def open_help():
    webbrowser.open("https://github.com/iamironman0/youtube_downloader/issues")


class YouTubeDownloader(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("YouTube Downloader")
        self.geometry("800x500")
        self.resizable(False, False)
        self.iconbitmap(LOGO)

        self.center_window(800, 500)
        self.grid_columnconfigure(0, weight=1)

        self.progress_text = None
        self.progress = None
        self.quality_option = None
        self.format_option = None

        self.playlist_title = ""
        self.playlist_video_count = None
        self.playlist_views = None
        self.playlist_last_updated = None
        self.playlist_videos = None

        self.video_quality = []
        self.audio_quality = []

        self.search_result = {}

        self.page_one()

        self.protocol("WM_DELETE_WINDOW", on_close)

    def page_one(self):
        title = ctk.CTkLabel(self, text="YouTube Downloader", font=FONTS["title"])
        title.grid(row=0, column=0, padx=20, pady=40, sticky="ew")

        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.grid(row=1, column=0, padx=60, pady=(40, 0), sticky="nsew")
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=1)
        frame.grid_columnconfigure(2, weight=1)

        icon_one = ctk.CTkLabel(frame, text="", image=ICONS["paste"])
        icon_one.grid(row=0, column=0, padx=(50, 0), pady=0, sticky="w")
        icon_two = ctk.CTkLabel(frame, text="", image=ICONS["videos"])
        icon_two.grid(row=0, column=1, padx=20, pady=0, sticky="ew")
        icon_three = ctk.CTkLabel(frame, text="", image=ICONS["download"])
        icon_three.grid(row=0, column=2, padx=(0, 60), pady=0, sticky="e")

        frame2 = ctk.CTkFrame(self, fg_color="transparent")
        frame2.grid(row=2, column=0, padx=60, pady=0, sticky="nsew")
        frame2.grid_columnconfigure(0, weight=1)
        frame2.grid_columnconfigure(1, weight=1)
        frame2.grid_columnconfigure(2, weight=1)

        label_one = ctk.CTkLabel(frame2, text="  Paste Video", image=ICONS["one"], compound="left", font=FONTS["large"])
        label_one.grid(row=0, column=0, padx=20, pady=0, sticky="w")
        label_two = ctk.CTkLabel(frame2, text="  Select Video", image=ICONS["two"], compound="left",
                                 font=FONTS["large"])
        label_two.grid(row=0, column=1, padx=20, pady=0, sticky="ew")
        label_three = ctk.CTkLabel(frame2, text="   Download Video", image=ICONS["three"], compound="left",
                                   font=FONTS["large"])
        label_three.grid(row=0, column=2, padx=20, pady=0, sticky="e")

        frame3 = ctk.CTkFrame(self, fg_color="transparent", height=100)
        frame3.grid(row=3, column=0, padx=60, pady=(5, 20), sticky="nsew")
        frame3.grid_columnconfigure(0, weight=1)
        frame3.grid_columnconfigure(1, weight=1)
        frame3.grid_columnconfigure(2, weight=1)
        frame3.grid_propagate(False)

        text_one = ctk.CTkLabel(frame3, text="Paste link YouTube or enter keyword into the search box.",
                                font=FONTS["small"], justify="left", wraplength=200)
        text_one.grid(row=0, column=0, padx=20, pady=0, sticky="w")
        text_two = ctk.CTkLabel(frame3,
                                text="Select the MP4 or MP3 format you want and then click the Download button.",
                                font=FONTS["small"], justify="left", wraplength=200)
        text_two.grid(row=0, column=1, padx=20, pady=0, sticky="ew")
        text_three = ctk.CTkLabel(frame3,
                                  text="Wait a few seconds for the conversion to complete and click Download to "
                                       "download the file to your device.",
                                  font=FONTS["small"], justify="left", wraplength=200)
        text_three.grid(row=0, column=2, padx=(30, 0), pady=5, sticky="e")

        frame4 = ctk.CTkFrame(self, fg_color="transparent")
        frame4.grid(row=4, column=0, padx=60, pady=10, sticky="ew")
        frame4.grid_columnconfigure(0, weight=1)

        start_btn = ctk.CTkButton(frame4, text="Start Downloading", height=40, font=FONTS["large"], corner_radius=5,
                                  command=lambda: self.switch_page("page_two"))
        start_btn.grid(row=0, column=0, padx=100, pady=0, sticky="ew")

    def page_two(self):
        title = ctk.CTkLabel(self, text="Select Download Mode", font=FONTS["title"])
        title.grid(row=0, column=0, padx=20, pady=(100, 20), sticky="ew")

        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.grid(row=1, column=0, padx=60, pady=20, sticky="nsew")

        btn_one = ctk.CTkButton(frame, text="Single Video", image=ICONS["video"], compound="top",
                                font=FONTS["subtitle"], width=300, height=150, corner_radius=5,
                                command=lambda: self.switch_page("single_video_page"), fg_color="transparent",
                                hover=False, border_width=2, text_color=("black", "white"))
        btn_one.grid(row=0, column=0, padx=20, pady=20, sticky="e")
        btn_two = ctk.CTkButton(frame, text="Playlist", image=ICONS["playlist"], compound="top", font=FONTS["subtitle"],
                                width=300, height=150, corner_radius=5,
                                command=lambda: self.switch_page("playlist_page"), fg_color="transparent", hover=False,
                                border_width=2, text_color=("black", "white"))
        btn_two.grid(row=0, column=1, padx=20, pady=20, sticky="w")

        help_btn = ctk.CTkButton(frame, text="Get Help", height=30, font=FONTS["normal"], corner_radius=5,
                                 command=open_help)
        help_btn.grid(row=1, column=0, padx=20, pady=20, sticky="w")

    def single_video_page(self):
        title = ctk.CTkLabel(self, text="Single Video Downloader", font=FONTS["title"])
        title.grid(row=0, column=0, padx=20, pady=20, sticky="w")

        back_btn = ctk.CTkButton(self, text="Back", corner_radius=5, command=lambda: self.switch_page("page_two"))
        back_btn.grid(row=0, column=1, padx=20, pady=20, sticky="e")

        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.grid(row=1, column=0, padx=40, pady=20, sticky="ew", columnspan=2)
        frame.grid_columnconfigure(0, weight=1)

        search_entry = ctk.CTkEntry(frame, placeholder_text="Search or paste YouTube link here", width=500, height=50,
                                    corner_radius=5, border_width=2)
        search_entry.grid(row=0, column=0, padx=0, pady=5, sticky="w")

        search_btn = ctk.CTkButton(frame, text="Search", width=200, height=50, corner_radius=5,
                                   command=lambda: self.search_video(url=search_entry.get()), font=FONTS["large"])
        search_btn.grid(row=0, column=1, padx=0, pady=5, sticky="e")

    def playlist_page(self):
        title = ctk.CTkLabel(self, text="Playlist Downloader", font=FONTS["title"])
        title.grid(row=0, column=0, padx=20, pady=20, sticky="w")

        back_btn = ctk.CTkButton(self, text="Back", corner_radius=5, command=lambda: self.switch_page("page_two"))
        back_btn.grid(row=0, column=1, padx=20, pady=20, sticky="e")

        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.grid(row=1, column=0, padx=40, pady=20, sticky="ew", columnspan=2)
        frame.grid_columnconfigure(0, weight=1)

        search_entry = ctk.CTkEntry(frame, placeholder_text="Search or paste YouTube link here", width=500, height=50,
                                    corner_radius=5, border_width=2)
        search_entry.grid(row=0, column=0, padx=0, pady=5, sticky="w")

        search_btn = ctk.CTkButton(frame, text="Search", width=200, height=50, corner_radius=5,
                                   command=lambda: self.search_playlist(url=search_entry.get()), font=FONTS["large"])
        search_btn.grid(row=0, column=1, padx=0, pady=5, sticky="e")

    def result_widgets(self):
        if self.search_result:
            frame2 = ctk.CTkFrame(self, fg_color="transparent", height=50)
            frame2.grid(row=2, column=0, padx=40, pady=(20, 0), sticky="ew")
            frame2.grid_propagate(False)

            self.format_option = ctk.CTkOptionMenu(frame2, values=["Video", "Audio"], command=self.update_quality)
            self.format_option.grid(row=0, column=1, padx=10, pady=(0, 20))

            self.quality_option = ctk.CTkOptionMenu(frame2, values=self.video_quality)
            self.quality_option.grid(row=0, column=2, padx=10, pady=(0, 20))

            download_btn = ctk.CTkButton(frame2, text="Download", command=self.start_download)
            download_btn.grid(row=0, column=3, padx=10, pady=(0, 20))

            frame3 = ctk.CTkFrame(self, fg_color="transparent", height=250)
            frame3.grid(row=3, column=0, padx=40, pady=(0, 20), sticky="nsew")
            frame3.grid_propagate(False)

            thumbnail = ctk.CTkImage(Image.open(f"{CURRENT_PATH}\\assets\\downloads\\thumbnail.jpg"),
                                     Image.open(f"{CURRENT_PATH}\\assets\\downloads\\thumbnail.jpg"), (300, 150))

            video_thumbnail = ctk.CTkLabel(frame3, text="", width=300, height=150, image=thumbnail)
            video_thumbnail.grid(row=0, column=0, padx=0, pady=20, sticky="w")

            video_title = ctk.CTkLabel(frame3, text=self.search_result.get("title"), font=FONTS["large"],
                                       wraplength=400)
            video_title.grid(row=0, column=1, padx=10, pady=20)
        else:
            error_message = ctk.CTkLabel(self, text="Video not found", image=ICONS["not_found"], compound="top",
                                         font=FONTS["subtitle"])
            error_message.grid(row=2, column=0, padx=20, pady=20)

    def playlist_result_widgets(self):
        if self.playlist_title:
            frame = ctk.CTkFrame(self, fg_color="transparent")
            frame.grid(row=2, column=0, padx=40, pady=(20, 0), sticky="nsew")

            thumbnail = ctk.CTkImage(Image.open(f"{CURRENT_PATH}\\assets\\downloads\\thumbnail.jpg"),
                                     Image.open(f"{CURRENT_PATH}\\assets\\downloads\\thumbnail.jpg"), (300, 150))

            video_thumbnail = ctk.CTkLabel(frame, text="", width=300, height=150, image=thumbnail)
            video_thumbnail.grid(row=0, column=0, padx=0, pady=5, sticky="w")

            video_title = ctk.CTkLabel(frame, text=self.playlist_title, font=FONTS["large"],
                                       wraplength=400)
            video_title.grid(row=0, column=1, padx=10, pady=5)

            frame2 = ctk.CTkFrame(self, fg_color="transparent")
            frame2.grid(row=3, column=0, padx=40, pady=(0, 20), sticky="ew")

            video_count = ctk.CTkLabel(frame2, text=f"{self.playlist_video_count} Videos", font=FONTS["normal"])
            video_count.grid(row=0, column=0, padx=(0, 10), pady=0)

            video_views = ctk.CTkLabel(frame2, text=f"{self.playlist_views} views", font=FONTS["normal"])
            video_views.grid(row=0, column=1, padx=10, pady=0)

            video_last_updated = ctk.CTkLabel(frame2, text=f"Last updated on {self.playlist_last_updated}",
                                              font=FONTS["normal"])
            video_last_updated.grid(row=0, column=2, padx=10, pady=0)

            download_btn = ctk.CTkButton(self, text="Download All", command=self.start_playlist_download)
            download_btn.grid(row=4, column=0, padx=40, pady=0, sticky="w")
        else:
            error_message = ctk.CTkLabel(self, text="Video not found", image=ICONS["not_found"], compound="top",
                                         font=FONTS["subtitle"])
            error_message.grid(row=2, column=0, padx=20, pady=20)

    def switch_page(self, page_name: str):
        if page_name == "page_one":
            self.destroy_widgets()
            self.after(500, self.page_one)
        elif page_name == "page_two":
            self.destroy_widgets()
            self.after(500, self.page_two)
        elif page_name == "single_video_page":
            self.destroy_widgets()
            self.after(500, self.single_video_page)

        elif page_name == "playlist_page":
            self.destroy_widgets()
            self.after(500, self.playlist_page)

    def start_playlist_download(self):
        threading.Thread(target=self.download_playlist_callback).start()

    def download_playlist_callback(self):
        download_path = fd.askdirectory()

        if not download_path:
            return

        self.destroy_widgets()
        self.playlist_loading()

        for video in self.playlist_videos:
            self.progress_text.configure(text=video.title)
            video_title = sanitize_filename(video.title)
            video.streams.get_highest_resolution().download(filename=f"{download_path}/{video_title}.mp4")

        self.destroy_widgets()

        msg = CTkMessagebox(master=self, title="Download Complete", message=f"Saved To: {download_path}",
                            corner_radius=8,
                            icon="check")

        if msg.get() == "OK" or msg.get() is None:
            self.destroy_widgets()
            self.after(500, self.playlist_page)

    def search_playlist(self, url: str):
        try:
            playlist = Playlist(url)
            self.playlist_title = playlist.title
            self.playlist_video_count = playlist.length
            self.playlist_views = playlist.views
            self.playlist_last_updated = playlist.last_updated
            thumbnail_url = ""

            for thumbnail in playlist.videos[:1]:
                thumbnail_url = thumbnail.thumbnail_url

            filename = f"{CURRENT_PATH}\\assets\\downloads\\thumbnail.jpg"
            urllib.request.urlretrieve(thumbnail_url, filename)

            self.playlist_videos = playlist.videos

            self.after(500, self.playlist_result_widgets)

        except KeyError:
            msg = CTkMessagebox(master=self, title="Error", message="Please provide a playlist url.",
                                corner_radius=8,
                                icon="cancel")

            if msg.get() == "OK" or msg.get() is None:
                self.destroy_widgets()
                self.after(100, self.playlist_page)

    def playlist_loading(self):
        frame = ctk.CTkFrame(self)
        frame.grid(row=1, column=0, padx=140, pady=150, sticky="nsew")
        frame.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(frame, text="Downloading...", font=FONTS["subtitle"])
        title.grid(row=0, column=0, padx=20, pady=20, sticky="w")

        self.progress_text = ctk.CTkLabel(frame, text="", font=FONTS["small"], wraplength=500)
        self.progress_text.grid(row=1, column=0, padx=20, pady=20, sticky="w")

        progress = ctk.CTkProgressBar(frame, mode="indeterminate", height=10, corner_radius=4)
        progress.grid(row=2, column=0, padx=20, pady=20, sticky="ew")
        progress.start()

    def loading(self):
        frame = ctk.CTkFrame(self)
        frame.grid(row=1, column=0, padx=200, pady=150, sticky="nsew")

        title = ctk.CTkLabel(frame, text="Downloading...", font=FONTS["subtitle"])
        title.grid(row=0, column=0, padx=20, pady=20, sticky="w")

        self.progress = ctk.CTkProgressBar(frame, mode="determinate", height=10, corner_radius=4)
        self.progress.set(0)
        self.progress.grid(row=1, column=0, padx=20, pady=20, sticky="ew")

        self.progress_text = ctk.CTkLabel(frame, text="0%", font=FONTS["normal"])
        self.progress_text.grid(row=1, column=1, padx=(0, 20), pady=20, sticky="e")

    def progress_callback(self, stream, chunk, bytes_remaining):
        total_size = stream.filesize
        bytes_downloaded = total_size - bytes_remaining

        percentage_of_completion = round((bytes_downloaded / total_size) * 100)

        float_range = percentage_of_completion / 100

        self.progress.set(float_range)
        self.progress_text.configure(text=f"{percentage_of_completion}%")
        self.update_idletasks()

    def complete_callback(self, stream, file_path):
        self.destroy_widgets()

        msg = CTkMessagebox(master=self, title="Download Complete", message=f"Saved To: {file_path}", corner_radius=8,
                            icon="check")

        if msg.get() == "OK" or msg.get() is None:
            self.destroy_widgets()
            self.after(500, self.single_video_page)

    def start_download(self):
        threading.Thread(target=self.download_callback).start()

    def download_callback(self):
        quality = self.quality_option.get()
        yt = YouTube(self.search_result["url"], on_complete_callback=self.complete_callback,
                     on_progress_callback=self.progress_callback)

        format_option = self.format_option.get()
        file_extension = "mp4" if format_option == "Video" else "mp3"
        file_name = fd.asksaveasfilename(initialfile=f"{yt.title}", defaultextension=file_extension)

        if not file_name:
            return

        if format_option == "Video":
            stream = yt.streams.filter(progressive=True, resolution=quality).first()
        else:
            stream = yt.streams.filter(only_audio=True, abr=quality).first()

        self.destroy_widgets()
        self.loading()

        stream.download(filename=file_name)

    def configure_quality(self, quality_list):
        self.quality_option.configure(values=quality_list)
        self.quality_option.set(quality_list[0])

    def update_quality(self, value):
        if value == "Audio":
            self.configure_quality(self.audio_quality)
        else:
            self.configure_quality(self.video_quality)

    def handle_error(self):
        msg = CTkMessagebox(master=self, title="Error", message="Video unavailable.",
                            corner_radius=8,
                            icon="cancel")

        if msg.get() == "OK" or msg.get() is None:
            self.destroy_widgets()
            self.after(500, self.single_video_page)

    def search_video_url(self, url: str):
        try:
            video = YouTube(url)
            self.search_result["title"] = video.title
            self.search_result["thumbnail"] = video.thumbnail_url
            self.search_result["url"] = video.watch_url
        except exceptions.PytubeError:
            self.handle_error()

    def search_video_title(self, title: str):
        try:
            video = Search(title)
            if video:
                result = video.results[0]
                self.search_result["title"] = result.title
                self.search_result["thumbnail"] = result.thumbnail_url
                self.search_result["url"] = result.watch_url
        except exceptions.PytubeError:
            self.handle_error()

    def search_video(self, url: str):
        if url:
            if url.startswith("https://"):
                self.search_video_url(url)
            else:
                self.search_video_title(url)

            yt = YouTube(self.search_result.get("url"))
            video_streams = yt.streams.filter(progressive=True)
            self.video_quality.clear()
            for stream in video_streams:
                self.video_quality.append(stream.resolution)

            audio_streams = yt.streams.filter(only_audio=True)
            self.audio_quality.clear()
            for stream in audio_streams:
                self.audio_quality.append(stream.abr)

            self.download_thumbnail()
            self.result_widgets()
        else:
            msg = CTkMessagebox(master=self, title="Warning", message="Please provide url or video title",
                                corner_radius=8,
                                icon="warning")

            if msg.get() == "OK" or msg.get() is None:
                self.destroy_widgets()
                self.after(500, self.single_video_page)

    def download_thumbnail(self):
        thumbnail_url = self.search_result.get("thumbnail")
        filename = f"{CURRENT_PATH}\\assets\\downloads\\thumbnail.jpg"

        urllib.request.urlretrieve(thumbnail_url, filename)

    def destroy_widgets(self):
        widgets = self.winfo_children()
        for widget in widgets:
            widget.grid_forget()

    def center_window(self, width: int, height: int):
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        window_height = int((screen_width / 2) - (width / 2))
        window_width = int((screen_height / 2) - (height / 2))
        self.geometry(f"{width}x{height}+{window_height}+{window_width}")


if __name__ == "__main__":
    app = YouTubeDownloader()
    app.mainloop()
