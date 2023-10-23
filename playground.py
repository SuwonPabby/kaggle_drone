def get_route_df(mode, batch=3, path=None):
    if mode == "LOAD":
        return pd.read_pickle(path)
    elif mode == "CREATE":
        for wh in warehouse_df.index:
            idx = list(np.where(from_wh_df == wh))
            priority_df = orders_df.loc[idx[0], :]

            priority_df = priority_df.sort_values(
                by=f"weight_dist_{wh}")
            idx[0] = np.array(priority_df.index)
            batch_split = np.linspace(0, len(idx[0]), batch+1, dtype=int)
            for batch_idx in range(batch):
                batch_order_idx = idx[0][batch_split[batch_idx]
                    :batch_split[batch_idx+1]]

                # Get wh_distance_matrix
                wh_distance_matrix = distance_matrix.copy()
                wh_distance_matrix[:len(orders_df), len(orders_df) + wh] = 0
                wh_distance_matrix = wh_distance_matrix[np.ix_(
                    np.append(batch_order_idx, len(orders_df) + wh),
                    np.append(batch_order_idx, len(orders_df) + wh))]
                display(wh_distance_matrix.shape)
                break
                # Get wh_demand_info
                wh_demand_info = {}
                for order, item in zip(idx[0], idx[1]):
                    if order not in wh_demand_info.keys():
                        wh_demand_info[order] = 0
                    wh_demand_info[order] += product_df.loc[item, "weight"]

                # Make Routing Model
                manager = pywrapcp.RoutingIndexManager(
                    len(wh_distance_matrix),
                    len(idx[0]),
                    len(wh_distance_matrix) - 1
                )

                routing = pywrapcp.RoutingModel(manager)

                def distance_callback(from_index, to_index):
                    from_node = manager.IndexToNode(from_index)
                    to_node = manager.IndexToNode(to_index)
                    return wh_distance_matrix[from_node][to_node]
                transit_callback_index = routing.RegisterTransitCallback(
                    distance_callback)
                routing.SetArcCostEvaluatorOfAllVehicles(
                    transit_callback_index)

                break


get_route_df(mode="CREATE")
