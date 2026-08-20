import { ObjectId } from 'bson';

export const shapeIntoMongoDbjectId = (target: any) => {
	return typeof target === 'string' ? new Object(target) : target;
};
