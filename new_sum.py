attachment_traverser = LlmAgent(
    name="AttachmentTraverser",
    model=HelixGemini(model=MODEL),
    description="Finds attachment IDs from arb_attachment_links using node_id",
    instruction="""
    You are the Attachment Traverser.

    Inputs in session state:
    - node_results (JSON) → extract the node_id from here

    Steps:
    1. Read node_id from node_results
    2. Call `query_graph` to search arb_attachment_links
       WHERE node_id = {node_id}
    3. Extract all attachment_ids from results
    4. Call `record_attachment_ids` with the list
    
    If no attachment_links found, record empty list 
    and note the failure.
    """,
    tools=[FunctionTool(query_graph), 
           FunctionTool(record_attachment_ids)],
    output_key="attachment_ids",
)

summary_fetcher = LlmAgent(
    name="SummaryFetcher",
    model=HelixGemini(model=MODEL),
    description="Fetches summaries from arb_attachments using attachment_ids",
    instruction="""
    You are the Summary Fetcher.

    Inputs in session state:
    - attachment_ids (list)

    Steps:
    1. Read attachment_ids from state
    2. For each attachment_id, call `query_graph`
       to fetch from arb_attachments WHERE id = {attachment_id}
    3. Collect all summary fields
    4. Call `record_attachment_summaries` with all summaries
    
    If attachment_ids is empty, record that no 
    summaries were found.
    """,
    tools=[FunctionTool(query_graph),
           FunctionTool(record_attachment_summaries)],
    output_key="attachment_summaries",
)


refinement_loop = LoopAgent(
    name="GraphRefinementLoop",
    sub_agents=[
        node_finder,
        context_gatherer,
        attachment_traverser,  # 👈 new
        summary_fetcher,        # 👈 new
        answer_generator,
        result_checker,
    ],
    max_iterations=MAX_ITERATIONS,
)


- attachment_ids
- attachment_summaries


"""
Inputs in session state:
- user_question
- classification
- node_results (JSON)
- edge_results (JSON)
- attachment_summaries (JSON)  # 👈 new

Steps:
...
2. If classification is `arb_summary`, combine 
   node_results with attachment_summaries to write
   a concise project summary. Cite attachment names/ids.
"""




instruction="""
First check `classification` in session state.
If classification != 'arb_summary', 
call `record_attachment_ids` with empty list and stop.
Otherwise proceed with the traversal.
"""
