package backends

import (
	"github.com/docker/docker/api/types/filters"
	timetypes "github.com/docker/docker/api/types/time"
	"fmt"
	"time"
)

func getUntilFromPruneFilters(pruneFilters filters.Args) (time.Time, error) {
	until := time.Time{}
	if !pruneFilters.Include("until") {
		return until, nil
	}
	untilFilters := pruneFilters.Get("until")
	if len(untilFilters) > 1 {
		return until, fmt.Errorf("more than one until filter specified")
	}
	ts, err := timetypes.GetTimestamp(untilFilters[0], time.Now())
	if err != nil {
		return until, err
	}
	seconds, nanoseconds, err := timetypes.ParseTimestamps(ts, 0)
	if err != nil {
		return until, err
	}
	until = time.Unix(seconds, nanoseconds)
	return until, nil
}

func matchLabels(pruneFilters filters.Args, labels map[string]string) bool {
	if !pruneFilters.MatchKVList("label", labels) {
		return false
	}
	// By default MatchKVList will return true if field (like 'label!') does not exist
	// So we have to add additional Include("label!") check
	if pruneFilters.Include("label!") {
		if pruneFilters.MatchKVList("label!", labels) {
			return false
		}
	}
	return true
}