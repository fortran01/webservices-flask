#!/bin/bash

# Initialize a counter for the total time the string is seen and a flag to track if the string is being seen
total_time_seen=0
string_seen=false

# Start an infinite loop to continuously check the output of lsof
while true; do
  # Check if the specific string exists in the output of lsof
  if lsof -a -n -Pi | grep -q '127.0.0.1:5000->'; then
    if [ "$string_seen" = false ]; then
      string_seen=true
    fi
    # Increment the counter since the string is seen
    ((total_time_seen++))
  else
    if [ "$string_seen" = true ]; then
      # Display the total time the string has been seen only if it was previously seen
      echo "Total time seen: $total_time_seen seconds."
      break # Exit the loop if the string is not seen anymore
    fi
  fi
  
  # Wait for 1 second before checking again
  sleep 1
done
