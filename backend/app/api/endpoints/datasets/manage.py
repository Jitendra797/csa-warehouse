from fastapi import APIRouter

manage_router = APIRouter()

# @manage_router.get("/dataset/{user_id}")
# def get_user_datasets():
#     return {
#         "message": "will return all user datasets"
#     }


@manage_router.put("/datasets/{dataset_id}/edit")
def edit_dataset(dataset_id):
    return {"message": "will edit an existing dataset"}


@manage_router.delete("/datasets/{dataset_id}")
def delete_dataset(dataset_id):
    return {"message": "will delete a dataset"}
