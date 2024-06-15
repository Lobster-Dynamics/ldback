from domain.events import DocumentCreatedEvent

from .observer import Observer

from .subscribers import DocumentUploadedNotifier
from .subscribers.document_created_notifier import INotifier

def create_app_observer(concrete_notifier: INotifier)-> Observer:
    observer = Observer()
    observer.add_listener(
        DocumentUploadedNotifier(concrete_notifier), DocumentCreatedEvent
    )
    return observer