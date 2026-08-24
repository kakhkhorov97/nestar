import { ObjectId } from 'bson';

export const availableAgentSorts = ['createdAt', 'updatedAt', 'memberLikes', 'memberViews', 'memberRank'];
export const availableMemberSorts = ['createdAt', 'updatedAt', 'memberLikes', 'memberViews'];

export const shapeIntoMongoDbjectId = (target: any) => {
	return typeof target === 'string' ? new Object(target) : target;
};
