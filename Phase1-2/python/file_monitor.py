import os
import threading
import time
from watchfiles import watch, Change
import config

class FileMonitor:
    def __init__(self, target_dir, rag_engine, on_change_callback=None):
        self.target_dir = os.path.abspath(target_dir)
        self.rag = rag_engine
        self.on_change_callback = on_change_callback
        self.running = False
        self.thread = None

    def start(self):
        if self.running: return
        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False

    def _run(self):
        print(f"[Monitor] Starting watcher on {self.target_dir}")
        for changes in watch(self.target_dir):
            if not self.running: break
            
            for change_type, path in changes:
                path = os.path.abspath(path)
                filename = os.path.basename(path)
                
                # We only care about changes within DATA_DIR for security
                if not path.startswith(self.target_dir):
                    continue

                if change_type == Change.added:
                    print(f"[Monitor] Added: {filename}")
                    if os.path.isfile(path):
                        content = self.rag._read_file_content(path)
                        if content:
                            self.rag.add_text(
                                f"Content of file '{filename}':\n{content[:2000]}",
                                metadata={"type": "file_content", "filename": filename, "path": path},
                                doc_id=f"file_content_{filename}"
                            )
                
                elif change_type == Change.deleted:
                    print(f"[Monitor] Deleted: {filename}")
                    self.rag.delete_file_content(filename)
                
                elif change_type == Change.modified:
                    print(f"[Monitor] Modified: {filename}")
                    if os.path.isfile(path):
                        content = self.rag._read_file_content(path)
                        if content:
                            self.rag.add_text(
                                f"Content of file '{filename}':\n{content[:2000]}",
                                metadata={"type": "file_content", "filename": filename, "path": path},
                                doc_id=f"file_content_{filename}"
                            )

                # Trigger UI refresh if callback exists
                if self.on_change_callback:
                    self.on_change_callback(change_type.name, filename)

if __name__ == "__main__":
    # Test stub
    from rag_engine import RAGEngine
    r = RAGEngine()
    fm = FileMonitor(config.IMAGES_DIR, r, lambda t, f: print(f"UI Callback: {t} {f}"))
    fm.start()
    try:
        while True: time.sleep(1)
    except KeyboardInterrupt:
        fm.stop()
