import { Args, Mutation, Query, Resolver } from '@nestjs/graphql';

import { AuthMember } from '../auth/decorators/authMember.decorator';
import { AuthGuard } from '../auth/guards/auth.guard';
import { UseGuards } from '@nestjs/common';
import type { ObjectId } from 'mongoose';
import { CommentService } from './comment.service';

import { WithoutGuard } from '../auth/guards/without.guard';
import { RolesGuard } from '../auth/guards/roles.guard';

import { Roles } from '../auth/decorators/roles.decorator';
import { CommentInput, CommentsInquiry } from '../../libs/dto/comment/comment.input';
import { CommentUpdate } from '../../libs/dto/comment/comment.update';
import { shapeIntoMongoDbjectId } from '../../libs/config';
import { Comment as CommentDTO, Comments } from '../../libs/dto/comment/comment';
import { MemberType } from '../../libs/enums/member.enum';

@Resolver()
export class CommentResolver {
	constructor(private readonly commentService: CommentService) {}

	@UseGuards(AuthGuard)
	@Mutation(() => CommentDTO)
	public async createComment(
		@Args('input') input: CommentInput,
		@AuthMember('_id') memberId: ObjectId,
	): Promise<CommentDTO> {
		console.log('Mutation: createComment');
		return await this.commentService.createComment(memberId, input);
	}

	@UseGuards(AuthGuard)
	@Mutation(() => CommentDTO)
	public async updateComment(
		@Args('input') input: CommentUpdate,
		@AuthMember('_id') memberId: ObjectId,
	): Promise<CommentDTO> {
		console.log('Mutation: updateComment');
		input._id = shapeIntoMongoDbjectId(input._id);
		return await this.commentService.updateComment(memberId, input);
	}

	@UseGuards(WithoutGuard)
	@Query(() => Comments)
	public async getComments(
		@Args('input') input: CommentsInquiry,
		@AuthMember('_id') memberId: ObjectId,
	): Promise<Comments> {
		console.log('Query: getComments');
		input.search.commentRefId = shapeIntoMongoDbjectId(input.search.commentRefId);
		const result = await this.commentService.getComments(memberId, input);
		return result;
	}

	/** ADMIN **/

	@Roles(MemberType.ADMIN)
	@UseGuards(RolesGuard)
	@Mutation(() => CommentDTO)
	public async removeCommentByAdmin(@Args('commentId') input: string): Promise<CommentDTO> {
		console.log('Mutation: removeCommentByAdmin');
		const commentId = shapeIntoMongoDbjectId(input);
		return await this.commentService.removeCommentByAdmin(commentId);
	}
}
