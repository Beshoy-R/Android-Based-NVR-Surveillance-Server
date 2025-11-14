import { useRef, useState } from "react";
import { ZoomIn, ZoomOut, Clock } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Recording } from "@/types/recordings";
import { cn } from "@/lib/utils";

interface TimelineProps {
  recordings: Recording[];
  onRecordingSelect: (recording: Recording) => void;
  selectedRecording: Recording | null;
}

export const Timeline = ({
  recordings,
  onRecordingSelect,
  selectedRecording,
}: TimelineProps) => {
  const [zoom, setZoom] = useState(1);
  const scrollRef = useRef<HTMLDivElement>(null);

  const zoomIn = () => setZoom((z) => Math.min(z + 0.5, 3));
  const zoomOut = () => setZoom((z) => Math.max(z - 0.5, 0.5));

  // Calculate position for each recording (0-24 hours = 0-100%)
  const getPosition = (time: string) => {
    const [hours, minutes] = time.split(":").map(Number);
    const totalMinutes = hours * 60 + minutes;
    return (totalMinutes / (24 * 60)) * 100;
  };

  const getWidth = (duration: number) => {
    // Duration in seconds, convert to percentage of 24 hours
    const minutes = duration / 60;
    return (minutes / (24 * 60)) * 100;
  };

  return (
    <div className="bg-card rounded-lg border border-border">
      <div className="flex items-center justify-between p-4 border-b border-border">
        <div className="flex items-center gap-2">
          <Clock className="h-5 w-5 text-muted-foreground" />
          <h3 className="text-lg font-semibold">Daily Timeline</h3>
          <span className="text-sm text-muted-foreground">
            ({recordings.length} recording{recordings.length !== 1 ? "s" : ""})
          </span>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="icon"
            onClick={zoomOut}
            disabled={zoom <= 0.5}
            className="bg-secondary hover:bg-secondary/80"
          >
            <ZoomOut className="h-4 w-4" />
          </Button>
          <span className="text-sm text-muted-foreground w-12 text-center">
            {zoom.toFixed(1)}x
          </span>
          <Button
            variant="outline"
            size="icon"
            onClick={zoomIn}
            disabled={zoom >= 3}
            className="bg-secondary hover:bg-secondary/80"
          >
            <ZoomIn className="h-4 w-4" />
          </Button>
        </div>
      </div>

      <div className="p-4">
        {/* Hour markers */}
        <div className="relative h-8 mb-2">
          <div
            className="flex justify-between text-xs text-muted-foreground"
            style={{ width: `${100 * zoom}%` }}
          >
            {Array.from({ length: 25 }).map((_, i) => (
              <span key={i} className="w-0">
                {i}:00
              </span>
            ))}
          </div>
        </div>

        {/* Timeline */}
        <div
          ref={scrollRef}
          className="overflow-x-auto"
          style={{ maxHeight: "400px" }}
        >
          <div
            className="relative h-24 bg-nvr-timeline-bg rounded-lg"
            style={{ width: `${100 * zoom}%`, minWidth: "100%" }}
          >
            {/* Grid lines for each hour */}
            {Array.from({ length: 24 }).map((_, i) => (
              <div
                key={i}
                className="absolute top-0 bottom-0 border-l border-border/30"
                style={{ left: `${(i / 24) * 100}%` }}
              />
            ))}

            {/* Recording clips */}
            {recordings.map((recording) => {
              const left = getPosition(recording.startTime);
              const width = getWidth(recording.duration);
              const isSelected = selectedRecording?.id === recording.id;

              return (
                <button
                  key={recording.id}
                  onClick={() => onRecordingSelect(recording)}
                  className={cn(
                    "absolute top-2 bottom-2 rounded transition-all hover:scale-105",
                    isSelected
                      ? "bg-primary ring-2 ring-primary shadow-lg z-10"
                      : "bg-nvr-clip-bg hover:bg-nvr-clip-bg/80"
                  )}
                  style={{
                    left: `${left}%`,
                    width: `${Math.max(width, 0.5)}%`,
                  }}
                  title={`${recording.startTime} - ${recording.endTime}`}
                >
                  <div className="h-full flex flex-col items-center justify-center px-2">
                    <span className="text-xs font-medium truncate w-full text-center">
                      {recording.startTime}
                    </span>
                    <span className="text-[10px] text-muted-foreground">
                      {Math.floor(recording.duration / 60)}m
                    </span>
                  </div>
                </button>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
};
