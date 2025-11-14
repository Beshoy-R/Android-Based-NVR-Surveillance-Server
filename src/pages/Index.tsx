import { useState } from "react";
import { CalendarView } from "@/components/Calendar/CalendarView";
import { VideoPlayer } from "@/components/VideoPlayer/VideoPlayer";
import { Timeline } from "@/components/Timeline/Timeline";
import { getDatesWithRecordings, getRecordingsForDate } from "@/data/mockRecordings";
import { Recording } from "@/types/recordings";
import { Video, Calendar as CalendarIcon } from "lucide-react";
import { Button } from "@/components/ui/button";

const Index = () => {
  const [selectedDate, setSelectedDate] = useState<Date | null>(null);
  const [selectedRecording, setSelectedRecording] = useState<Recording | null>(null);
  const [playbackSpeed, setPlaybackSpeed] = useState(1);
  const [showCalendar, setShowCalendar] = useState(true);

  const datesWithRecordings = getDatesWithRecordings();

  const handleDateSelect = (date: Date) => {
    setSelectedDate(date);
    const recordings = getRecordingsForDate(date);
    if (recordings.length > 0) {
      setSelectedRecording(recordings[0]);
      setShowCalendar(false);
    }
  };

  const handleRecordingSelect = (recording: Recording) => {
    setSelectedRecording(recording);
  };

  const handleBackToCalendar = () => {
    setShowCalendar(true);
    setSelectedDate(null);
    setSelectedRecording(null);
  };

  const recordings = selectedDate ? getRecordingsForDate(selectedDate) : [];

  return (
    <div className="min-h-screen bg-nvr-bg-dark">
      {/* Header */}
      <header className="bg-nvr-bg-darker border-b border-border">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-primary/10 rounded-lg">
                <Video className="h-6 w-6 text-primary" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-foreground">NVR Server</h1>
                <p className="text-sm text-muted-foreground">
                  Network Video Recorder
                </p>
              </div>
            </div>
            {!showCalendar && (
              <Button
                variant="outline"
                onClick={handleBackToCalendar}
                className="bg-secondary hover:bg-secondary/80"
              >
                <CalendarIcon className="h-4 w-4 mr-2" />
                Back to Calendar
              </Button>
            )}
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        {showCalendar ? (
          <div className="max-w-4xl mx-auto">
            <div className="text-center mb-8">
              <h2 className="text-3xl font-bold text-foreground mb-2">
                Recording Archive
              </h2>
              <p className="text-muted-foreground">
                Select a date to view recordings
              </p>
            </div>
            <CalendarView
              datesWithRecordings={datesWithRecordings}
              selectedDate={selectedDate}
              onDateSelect={handleDateSelect}
            />
          </div>
        ) : (
          <div className="space-y-6">
            {selectedRecording && (
              <>
                <div className="flex items-center justify-between">
                  <div>
                    <h2 className="text-2xl font-bold text-foreground">
                      {selectedDate?.toLocaleDateString("en-US", {
                        weekday: "long",
                        year: "numeric",
                        month: "long",
                        day: "numeric",
                      })}
                    </h2>
                    <p className="text-muted-foreground">
                      {selectedRecording.startTime} - {selectedRecording.endTime}
                    </p>
                  </div>
                </div>

                <VideoPlayer
                  videoUrl={selectedRecording.videoUrl}
                  playbackSpeed={playbackSpeed}
                  onPlaybackSpeedChange={setPlaybackSpeed}
                />

                <Timeline
                  recordings={recordings}
                  onRecordingSelect={handleRecordingSelect}
                  selectedRecording={selectedRecording}
                />
              </>
            )}
          </div>
        )}
      </main>
    </div>
  );
};

export default Index;
