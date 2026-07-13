        """"
        # cuisine filter
        if cuisine:
            cuisine_tags = tags.get("cuisine", "")
            cuisine_list = cuisine_tags.lower().split(";")

            if cuisine.lower() not in cuisine_list:
                continue
        """