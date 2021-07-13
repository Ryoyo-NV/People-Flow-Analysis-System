"""Module: Tracker Sort"""
#!/usr/bin/env python3

#pylint: disable=wrong-import-position

# class TrackerSort()
# Description: Handles the tracker sorting
# Parameter: None
# Return value: None
class TrackerSort():
    """Tracker sorting class"""

    # function __init__()
    # Description: class constructor
    # Parameter: None
    # Return value: None
    def __init__(self):
        """Class constructor"""

        self.__trk_id_cnt = 1       # Track id counter for new id generation

        # Tracker pool
        self.__trk_obj_id = []      # Pool for existing track ids (raw)
        self.__trk_id = []          # Pool for existing track ids
        self.__trk_no_update = []   # Pool for no update counters
        self.__trk_bb = []          # Pool for bounding boxes

        self.__obj_meta = None      # Holds the local copy of obj_meta

    # function update()
    # Description: Function that updates the details in tracker sort
    # Parameter: obj_meta
    # Return value: None
    def update(self, obj_meta):
        """Update tracker pool"""

        # Get local copy of obj_meta
        self.__obj_meta = obj_meta

        # Run tracker sort
        self.__sort()

    # function __sort()
    # Description: Function that sort the tracker pool
    # Parameter: None
    # Return value: None
    def __sort(self):
        """Sort object"""

        # Check if the object id exists
        if self.__obj_meta.object_id in self.__trk_obj_id:

            # Get index of the existing object information
            index = self.__trk_obj_id.index(self.__obj_meta.object_id)
            # Reset no update counter
            self.__trk_no_update[index] = 0
            # Update bounding box
            self.__trk_bb[index] = self.__get_bbox()

        else:

            # Add tracker sort item
            self.__add()

    # function __add()
    # Description: Function that adds new item in tracker sort
    # Parameter: None
    # Return value: None
    def __add(self):
        """Add tracker sort item"""

        # Add raw object id
        self.__trk_obj_id.append(self.__obj_meta.object_id)
        # Generate track id
        self.__trk_id.append(self.__get_new_id())
        # No update counter intial value is 0
        self.__trk_no_update.append(0)
        # Add bounding box
        self.__trk_bb.append(self.__get_bbox())

    # function __get_new_id()
    # Description: Function that generates track id for new tracker sort item
    # Parameter: None
    # Return value: trk_id
    def __get_new_id(self):
        """Get new track id"""

        # Get track id from counter
        trk_id = self.__trk_id_cnt

        # Increase the track id counter for next id generation
        self.__trk_id_cnt += 1

        # Return track id
        return trk_id

    # function __get_bbox()
    # Description: Function that extracts bounding box from obj meta
    # Parameter: None
    # Return value: bbox
    def __get_bbox(self):
        """Get bounding box from obj_meta"""

        # Extract bounding box details
        rect_params = self.__obj_meta.rect_params
        top = (rect_params.top)
        left = (rect_params.left)
        width = (rect_params.width)
        height = (rect_params.height)
        bbox = [left, top, left+width, top+height]

        # Return bounding box
        return bbox

    # function no_update_checker()
    # Description: Function that controls the tracker sort data based from no update counter
    # Parameter: None
    # Return value: None
    def no_update_checker(self):
        """Monitor the no update counter per tracked object"""

        # Begin from last index
        index = len(self.__trk_no_update) - 1
        while index >= 0:

            # Add 1 to no update counter
            self.__trk_no_update[index] += 1
            # Check if the no update counter exceeds
            if self.__trk_no_update[index] >= 120:
                # Delete tracker sort item
                del self.__trk_obj_id[index]
                del self.__trk_id[index]
                del self.__trk_no_update[index]
                del self.__trk_bb[index]

            # Move to next
            index -= 1

    # function get_tracked_list()
    # Description: Function that gets the list of detected object in the current frame
    # Parameter: None
    # Return value: trk_list
    def get_tracked_list(self):
        """Get the list of track id and bounding box of objects with detections"""

        trk_list = []       # Holds the list of detected object in the current frame

        # Check all no update counter
        index = 0
        while index < len(self.__trk_no_update):

            # Check if updated
            if self.__trk_no_update[index] == 0:

                # Add track id and bbox info
                trk_list.append([self.__trk_id[index], self.__trk_bb[index]])

            # Next
            index += 1

        # Return detected object list with track ids
        return trk_list
